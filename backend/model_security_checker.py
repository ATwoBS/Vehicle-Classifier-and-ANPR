import pickletools
import re
import io
import os
from typing import List, Set, Dict, Any
from pathlib import Path
import warnings

class ModelSecurityChecker:
    """
    Security checker for PyTorch models to prevent malicious code execution.
    Uses pickle opcode analysis to detect imports without executing the pickle.
    """
    
    def __init__(self, whitelist_file: str = "model_imports.whitelist"):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.whitelist_file = os.path.join(script_dir, whitelist_file)
        self.allowed_imports = self._load_whitelist()
        
    def _load_whitelist(self) -> List[str]:
        """Load and parse the whitelist file."""
        with open(self.whitelist_file, 'r') as f:
            lines = f.readlines()
            
        # Parse lines, ignore comments and empty lines
        whitelist = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                whitelist.append(line)
        
        return whitelist
    
    def _is_import_allowed(self, import_name: str) -> bool:
        """Check if an import matches any pattern in the whitelist."""
        if not import_name:
            return False
            
        for pattern in self.allowed_imports:
            # Convert glob-style pattern to regex
            regex_pattern = pattern.replace('*', '.*').replace('?', '.')
            if re.match(f'^{regex_pattern}$', import_name):
                return True
        return False
    
    def _analyze_pickle_opcodes(self, file_path: str) -> Set[str]:
        """
        Analyze pickle opcodes to extract import information without execution.
        This is safer than the previous approach.
        """
        imports = set()
        
        try:
            with open(file_path, 'rb') as f:
                # Reset file pointer
                f.seek(0)
                
                # Use pickletools to analyze the opcodes
                output = io.StringIO()
                try:
                    # pickletools.dis expects the file to be opened in binary mode
                    # but we need to handle the output correctly
                    pickletools.dis(f, output)
                    analysis = output.getvalue()
                except UnicodeDecodeError:
                    # If there's a Unicode error, try a different approach
                    f.seek(0)
                    # Read raw bytes and analyze manually
                    return self._manual_pickle_analysis(f.read())
                
                # Parse the disassembly to find GLOBAL opcodes
                lines = analysis.split('\n')
                module_stack = []  # Track modules for STACK_GLOBAL
                
                for line in lines:
                    line = line.strip()
                    
                    # Look for GLOBAL opcodes which indicate imports
                    if 'GLOBAL' in line and "'" in line:
                        # Extract the module and class from GLOBAL opcode
                        # Format: "    0: c    GLOBAL     'torch.nn.modules.conv Conv2d'"
                        try:
                            # Find the quoted part
                            start_quote = line.find("'")
                            end_quote = line.rfind("'")
                            if start_quote != -1 and end_quote != -1 and start_quote != end_quote:
                                import_info = line[start_quote+1:end_quote]
                                if ' ' in import_info:
                                    module, class_name = import_info.split(' ', 1)
                                    full_import = f"{module}.{class_name}"
                                    imports.add(full_import)
                                    imports.add(module)  # Also track just the module
                                else:
                                    imports.add(import_info)
                        except Exception:
                            continue
                    
                    # Track UNICODE opcodes for STACK_GLOBAL
                    elif 'UNICODE' in line and "'" in line:
                        try:
                            start_quote = line.find("'")
                            end_quote = line.rfind("'")
                            if start_quote != -1 and end_quote != -1 and start_quote != end_quote:
                                unicode_str = line[start_quote+1:end_quote]
                                module_stack.append(unicode_str)
                        except Exception:
                            continue
                    
                    # Handle STACK_GLOBAL which uses the last two items on stack
                    elif 'STACK_GLOBAL' in line and len(module_stack) >= 2:
                        try:
                            class_name = module_stack.pop()
                            module = module_stack.pop()
                            full_import = f"{module}.{class_name}"
                            imports.add(full_import)
                            imports.add(module)
                        except Exception:
                            continue
                
        except Exception as e:
            warnings.warn(f"Error analyzing pickle opcodes: {e}")
            # Try manual analysis as fallback
            try:
                with open(file_path, 'rb') as f:
                    imports.update(self._manual_pickle_analysis(f.read()))
            except Exception as e2:
                warnings.warn(f"Manual pickle analysis also failed: {e2}")
            
        return imports
    
    def _manual_pickle_analysis(self, pickle_data: bytes) -> Set[str]:
        """
        Manual analysis of pickle data when pickletools fails.
        Looks for common patterns in pickle files.
        """
        imports = set()
        
        try:
            # Look for common patterns that indicate imports
            data_str = pickle_data.decode('latin1', errors='ignore')
            
            # Common PyTorch/ML module patterns
            patterns = [
                r'torch\.nn\.modules\.(\w+)',
                r'torch\.(\w+)',
                r'torchvision\.(\w+)',
                r'numpy\.(\w+)',
                r'sklearn\.(\w+)',
                r'ultralytics\.(\w+)',
                r'transformers\.(\w+)'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, data_str)
                for match in matches:
                    if isinstance(match, tuple):
                        imports.add('.'.join(match))
                    else:
                        imports.add(match)
            
            # Look for explicit module names
            # Pickle files often contain module names as strings
            module_patterns = [
                r'(torch(?:\.\w+)*)',
                r'(numpy(?:\.\w+)*)',
                r'(sklearn(?:\.\w+)*)',
                r'(ultralytics(?:\.\w+)*)',
                r'(transformers(?:\.\w+)*)',
                r'(cv2(?:\.\w+)*)',
                r'(PIL(?:\.\w+)*)'
            ]
            
            for pattern in module_patterns:
                matches = re.findall(pattern, data_str)
                for match in matches:
                    if len(match) > 2:  # Avoid false positives from short matches
                        imports.add(match)
                        
        except Exception as e:
            warnings.warn(f"Manual pickle analysis failed: {e}")
            
        return imports
    
    def _extract_imports_from_torch_model(self, file_path: str) -> Set[str]:
        """
        Extract imports using PyTorch's safer loading mechanisms.
        """
        imports = set()
        
        try:
            import torch
            
            # Try to get model info without full loading
            with open(file_path, 'rb') as f:
                # Read the pickle header to understand the format
                magic_number = f.read(2)
                f.seek(0)
                
                if magic_number == b'\x80\x02':  # Pickle protocol 2
                    # This is a standard pickle file
                    imports.update(self._analyze_pickle_opcodes(file_path))
                
                # Try to load with weights_only=True (PyTorch 1.13+)
                try:
                    # This is safer as it only loads tensors, not arbitrary Python objects
                    checkpoint = torch.load(file_path, map_location='cpu', weights_only=True)
                    # If this succeeds, the model is likely safe
                    imports.add("torch.safe_load")
                except Exception:
                    # If weights_only fails, we need to analyze more carefully
                    imports.update(self._analyze_pickle_opcodes(file_path))
                    
        except ImportError:
            # Fallback to pickle analysis if torch is not available
            imports.update(self._analyze_pickle_opcodes(file_path))
        except Exception as e:
            warnings.warn(f"Error extracting imports from PyTorch model: {e}")
            
        return imports
    
    def check_model_file(self, model_path: str) -> Dict[str, Any]:
        """
        Check if a model file is safe to load based on its imports.
        
        Returns:
            dict: Security analysis results
        """
        print(f"🔍 Analyzing model file: {model_path}")
        
        try:
            # Try PyTorch-specific analysis first
            found_imports = self._extract_imports_from_torch_model(model_path)
            
            # If no imports found, try general pickle analysis
            if not found_imports:
                found_imports = self._analyze_pickle_opcodes(model_path)
                
        except Exception as e:
            return {
                'safe': False,
                'error': f"Failed to analyze file: {e}",
                'allowed_imports': [],
                'blocked_imports': [],
                'total_imports': 0
            }
        
        # Filter out empty/None values
        found_imports = {imp for imp in found_imports if imp and imp.strip()}
        
        # Categorize imports
        allowed_imports = []
        blocked_imports = []
        
        for imp in found_imports:
            if self._is_import_allowed(imp):
                allowed_imports.append(imp)
            else:
                blocked_imports.append(imp)
        
        is_safe = len(blocked_imports) == 0
        
        return {
            'safe': is_safe,
            'allowed_imports': sorted(allowed_imports),
            'blocked_imports': sorted(blocked_imports),
            'total_imports': len(found_imports),
            'whitelist_file': self.whitelist_file
        }
    
    def safe_load_model(self, model_path: str, force_load: bool = False):
        """
        Safely load a PyTorch model after security check.
        """
        # Perform security check first
        security_result = self.check_model_file(model_path)
        
        if not security_result['safe'] and not force_load:
            blocked = security_result['blocked_imports']
            raise SecurityError(
                f"Model contains potentially dangerous imports: {blocked}\n"
                f"Review your whitelist in {self.whitelist_file} or use force_load=True if you trust this model"
            )
        
        if security_result['blocked_imports']:
            warnings.warn(
                f"⚠️  Loading model with blocked imports: {security_result['blocked_imports']}"
            )
        
        # Try to load the model safely
        try:
            import torch
            
            # Try weights_only first (safest)
            try:
                model = torch.load(model_path, map_location='cpu', weights_only=True)
                print(f"✅ Model loaded safely with weights_only=True: {model_path}")
                return model
            except Exception:
                # Fall back to regular loading if weights_only fails
                if force_load or security_result['safe']:
                    model = torch.load(model_path, map_location='cpu')
                    print(f"✅ Model loaded: {model_path}")
                    return model
                else:
                    raise SecurityError("Model requires full pickle loading but failed security check")
                    
        except Exception as e:
            raise RuntimeError(f"Failed to load model: {e}")


class SecurityError(Exception):
    """Custom exception for security-related errors."""
    pass


def check_model_security(model_path: str, whitelist_file: str = "model_imports.whitelist") -> bool:
    """
    Convenience function to quickly check if a model is safe.
    """
    checker = ModelSecurityChecker(whitelist_file)
    result = checker.check_model_file(model_path)
    
    print(f"\n🔍 Security Analysis for {Path(model_path).name}")
    print(f"Status: {'✅ SAFE' if result['safe'] else '❌ POTENTIALLY UNSAFE'}")
    
    if 'error' in result:
        print(f"❌ Error: {result['error']}")
        return False
    
    print(f"Total imports detected: {result['total_imports']}")
    
    if result['allowed_imports']:
        print(f"✅ Allowed imports ({len(result['allowed_imports'])}):")
        for imp in result['allowed_imports'][:5]:  # Show first 5
            print(f"  ✓ {imp}")
        if len(result['allowed_imports']) > 5:
            print(f"  ... and {len(result['allowed_imports']) - 5} more")
    
    if result['blocked_imports']:
        print(f"❌ Blocked imports ({len(result['blocked_imports'])}):")
        for imp in result['blocked_imports']:
            print(f"  ✗ {imp}")
        print(f"\n💡 To allow these imports, add them to {result['whitelist_file']}")
    
    if result['total_imports'] == 0:
        print("ℹ️  No imports detected - this might be a weights-only file (safest)")
    
    return result['safe']

if __name__ == "__main__":
    # Example usage with improved path handling
    import sys
    
    if len(sys.argv) > 1:
        model_path = sys.argv[1]
    else:
        print("❌ Model file not found. Please specify the correct model path.")
    try:
        # Check the model
        is_safe = check_model_security(model_path)
        
        if is_safe:
            print(f"\n✅ {model_path} passed security check!")
        else:
            print(f"\n❌ {model_path} failed security check!")
            
    except Exception as e:
        print(f"Error: {e}")