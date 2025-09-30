import axios from "axios";

const API_URL = "http://127.0.0.1:5000"; // Flask Backend URL

export const uploadImage = async (file) => {
    const formData = new FormData();
    formData.append("image", file);

    return axios.post(`${API_URL}/upload`, formData, {
        headers: { "Content-Type": "multipart/form-data" }
    });
};
