import axios from "axios";

const API_URL=process.env.REACT_APP_API_URL;

export const uploadImage = async (file) => {
    const formData = new FormData();
    formData.append("image", file);

    return axios.post(`${API_URL}/upload`, formData, {
        headers: { "Content-Type": "multipart/form-data" }
    });
};
