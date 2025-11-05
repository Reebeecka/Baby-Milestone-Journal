import { useParams, useNavigate } from "react-router-dom";
import { useState } from "react";
import axios from "axios";

export default function Reset() {
    const { token } = useParams();
    const [password, setPassword] = useState("");
    const [msg, setMsg] = useState("");
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const res = await axios.post(`/api/reset/${token}`, { password });
            if (res.data.success) {
                setMsg("Lösenordet uppdaterat! Du kan nu logga in.");
                setTimeout(() => navigate("/"), 2000);
            } else setMsg(res.data.message);
        } catch {
            setMsg("Något gick fel. Försök igen.");
        }
    };

    return (
        <div className="flex justify-center items-center h-screen bg-pink-50">
            <form onSubmit={handleSubmit} className="bg-white p-8 rounded-2xl shadow-md w-80 text-center">
                <h2 className="text-2xl font-bold mb-4 text-pink-700">Återställ lösenord</h2>
                <input
                    type="password"
                    placeholder="Nytt lösenord"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    className="w-full p-2 border rounded-lg mb-4 focus:ring-2 focus:ring-pink-400 focus:outline-none"
                />
                <button className="w-full bg-pink-600 text-white py-2 rounded-lg font-semibold hover:bg-pink-700 transition">
                    Spara nytt lösenord
                </button>
                {msg && <p className="mt-4 text-gray-700">{msg}</p>}
            </form>
        </div>
    );
}
