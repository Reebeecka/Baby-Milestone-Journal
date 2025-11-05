import { useState } from "react";
import axios from "axios";
import { useNavigate, Link } from "react-router-dom";

export default function Login() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [msg, setMsg] = useState("");
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const res = await axios.post("/api/login", { email, password });
            if (res.data.success) {
                localStorage.setItem("user_id", res.data.user_id);
                navigate("/milestones");
            } else {
                setMsg(res.data.message);
            }
        } catch {
            setMsg("Något gick fel. Försök igen.");
        }
    };

    return (
        <div className="flex justify-center items-center h-screen bg-pink-50">
            <form
                onSubmit={handleSubmit}
                className="bg-white p-8 rounded-2xl shadow-md w-80 text-center"
            >
                <h1 className="text-2xl font-bold text-pink-700 mb-4">
                    Baby Milestone Journal 💕
                </h1>

                <input
                    className="border p-2 w-full rounded mb-3"
                    type="email"
                    placeholder="E-post"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                />

                <input
                    className="border p-2 w-full rounded mb-4"
                    type="password"
                    placeholder="Lösenord"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                />

                <button className="bg-pink-600 text-white w-full py-2 rounded hover:bg-pink-700 transition">
                    Logga in
                </button>

                {msg && <p className="text-center mt-3 text-gray-600">{msg}</p>}

                <div className="mt-6 text-center text-sm">
                    <Link
                        to="/forgot"
                        className="text-pink-700 hover:underline block mb-2"
                    >
                        Glömt lösenord?
                    </Link>

                    <p>
                        Har du inget konto?{" "}
                        <Link to="/register" className="text-pink-700 font-semibold hover:underline">
                            Registrera dig
                        </Link>
                    </p>
                </div>
            </form>
        </div>
    );
}
