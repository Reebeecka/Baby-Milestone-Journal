import { useState } from "react";
import axios from "axios";
import { Link } from "react-router-dom";

export default function Forgot() {
    const [email, setEmail] = useState("");
    const [sent, setSent] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        await axios.post("/api/forgot", { email });
        setSent(true);
    };

    if (sent) {
        return (
            <div className="flex justify-center items-center h-screen bg-pink-50">
                <div className="bg-white p-8 rounded-2xl shadow-md text-center max-w-md">
                    <div className="text-4xl mb-3">📧</div>
                    <h2 className="text-2xl font-bold text-pink-700 mb-3">Kolla din inkorg</h2>
                    <p className="text-gray-700 mb-6">
                        Om e-postadressen finns registrerad har vi skickat en länk för att återställa ditt lösenord.
                    </p>
                    <Link to="/" className="inline-block bg-pink-600 text-white px-5 py-2 rounded-lg font-semibold hover:bg-pink-700 transition">
                        Tillbaka till inloggning
                    </Link>
                </div>
            </div>
        );
    }

    return (
        <div className="flex justify-center items-center h-screen bg-pink-50">
            <form onSubmit={handleSubmit} className="bg-white p-8 rounded-2xl shadow-md w-80">
                <h2 className="text-2xl font-bold mb-4 text-pink-700 text-center">Glömt lösenord?</h2>
                <p className="text-gray-600 text-center mb-6">
                    Ange din e-postadress så skickar vi en återställningslänk.
                </p>
                <input type="email" placeholder="E-postadress" value={email}
                    onChange={(e) => setEmail(e.target.value)} required
                    className="w-full p-2 border rounded-lg focus:ring-2 focus:ring-pink-400 focus:outline-none mb-4" />
                <button type="submit" className="w-full bg-pink-600 text-white py-2 rounded-lg font-semibold hover:bg-pink-700 transition">
                    Skicka länk
                </button>
                <p className="mt-6 text-center text-sm">
                    <Link to="/" className="text-pink-700 hover:underline">← Tillbaka till inloggning</Link>
                </p>
            </form>
        </div>
    );
}
