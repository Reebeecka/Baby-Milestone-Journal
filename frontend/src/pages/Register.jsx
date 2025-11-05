import { useState } from "react";
import axios from "axios";
import { useNavigate, Link } from "react-router-dom";

export default function Register() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [msg, setMsg] = useState("");
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const res = await axios.post("/api/register", { email, password });
            if (res.data.success) {
                navigate("/");
            } else setMsg(res.data.message);
        } catch (err) {
            setMsg("E-postadressen används redan.");
        }
    };

    return (
        <div className="flex justify-center items-center h-screen bg-pink-50">
            <form onSubmit={handleSubmit} className="bg-white p-8 rounded-2xl shadow-md w-80">
                <h1 className="text-2xl font-bold text-center mb-6 text-pink-700">Skapa konto</h1>
                <input className="border p-2 w-full rounded mb-3" type="email" placeholder="E-post"
                    value={email} onChange={(e) => setEmail(e.target.value)} required />
                <input className="border p-2 w-full rounded mb-4" type="password" placeholder="Lösenord"
                    value={password} onChange={(e) => setPassword(e.target.value)} required />
                <button className="bg-pink-600 text-white w-full py-2 rounded hover:bg-pink-700">
                    Registrera
                </button>
                {msg && <p className="text-center mt-3 text-gray-600">{msg}</p>}
                <p className="mt-4 text-center text-sm">
                    Har du redan konto?{" "}
                    <Link to="/" className="text-pink-700 hover:underline">Logga in</Link>
                </p>
            </form>
        </div>
    );
}
