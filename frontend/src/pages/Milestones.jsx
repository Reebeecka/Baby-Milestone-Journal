import { useState, useEffect } from "react";
import axios from "axios";
import { Link, useNavigate } from "react-router-dom";

export default function Milestones() {
    const [milestones, setMilestones] = useState([]);
    const [title, setTitle] = useState("");
    const [description, setDescription] = useState("");
    const [date, setDate] = useState("");
    const [image, setImage] = useState(null);
    const [search, setSearch] = useState("");
    const [from, setFrom] = useState("");
    const [to, setTo] = useState("");
    const navigate = useNavigate();
    const user_id = localStorage.getItem("user_id");

    useEffect(() => {
        axios.get(`/api/milestones?user_id=${user_id}`).then((res) => {
            setMilestones(res.data);
        });
    }, [user_id]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        const formData = new FormData();
        formData.append("title", title);
        formData.append("description", description);
        formData.append("date", date);
        formData.append("user_id", user_id);
        if (image) formData.append("image", image);

        await axios.post("/api/add_milestone", formData, {
            headers: { "Content-Type": "multipart/form-data" },
        });

        setTitle("");
        setDescription("");
        setDate("");
        setImage(null);
        const res = await axios.get(`/api/milestones?user_id=${user_id}`);
        setMilestones(res.data);
    };

    // 🧠 Filterlogik
    const filtered = milestones.filter((m) => {
        const textMatch =
            m.title.toLowerCase().includes(search.toLowerCase()) ||
            m.description.toLowerCase().includes(search.toLowerCase());
        const dateObj = new Date(m.date);
        const inRange =
            (!from || dateObj >= new Date(from)) &&
            (!to || dateObj <= new Date(to));
        return textMatch && inRange;
    });

    return (
        <div className="min-h-screen bg-pink-50 p-6">
            <div className="max-w-2xl mx-auto">
                {/* Header */}
                <div className="flex justify-between items-center mb-6">
                    <h1 className="text-3xl font-bold text-pink-700">
                        Mina milstolpar
                    </h1>
                    <button
                        onClick={() => {
                            localStorage.clear();
                            navigate("/");
                        }}
                        className="text-sm text-pink-700 hover:underline"
                    >
                        Logga ut
                    </button>
                </div>

                {/* Formulär */}
                <form
                    onSubmit={handleSubmit}
                    className="bg-white p-4 rounded-lg shadow mb-6 space-y-3"
                >
                    <input
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                        placeholder="Titel"
                        className="w-full p-2 border rounded"
                        required
                    />
                    <input
                        value={date}
                        onChange={(e) => setDate(e.target.value)}
                        type="date"
                        className="w-full p-2 border rounded"
                        required
                    />
                    <textarea
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        placeholder="Beskrivning"
                        className="w-full p-2 border rounded"
                    />
                    <input
                        type="file"
                        onChange={(e) => setImage(e.target.files[0])}
                        className="w-full p-2 border rounded"
                        accept="image/*"
                    />

                    {/* Knappar */}
                    <div className="flex gap-3 justify-end items-center">
                        <Link
                            to="/stats"
                            className="bg-white text-pink-700 border border-pink-400 px-4 py-2 rounded hover:bg-pink-50 transition"
                        >
                            📊 Statistik
                        </Link>

                        <Link
                            to="/timeline"
                            className="bg-white text-pink-700 border border-pink-400 px-4 py-2 rounded hover:bg-pink-50 transition"
                        >
                            🕒 Se tidslinje
                        </Link>

                        <button className="bg-pink-600 text-white px-4 py-2 rounded hover:bg-pink-700">
                            + Lägg till milstolpe
                        </button>
                    </div>
                </form>

                {/* Sök och filter */}
                <div className="bg-white p-4 rounded-lg shadow mb-6 space-y-3">
                    <input
                        type="text"
                        placeholder="🔍 Sök milstolpe..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="w-full p-2 border rounded focus:ring-2 focus:ring-pink-300 outline-none"
                    />

                    <div className="flex gap-2">
                        <input
                            type="date"
                            value={from}
                            onChange={(e) => setFrom(e.target.value)}
                            className="border p-2 rounded w-1/2"
                        />
                        <input
                            type="date"
                            value={to}
                            onChange={(e) => setTo(e.target.value)}
                            className="border p-2 rounded w-1/2"
                        />
                    </div>
                </div>

                {/* Lista */}
                {filtered.length === 0 ? (
                    <p className="text-center text-gray-500">
                        Inga milstolpar matchar sökningen 💭
                    </p>
                ) : (
                    filtered.map((m) => (
                        <div key={m.id} className="bg-white p-4 rounded-lg shadow mb-4">
                            <h2 className="text-xl font-semibold">{m.title}</h2>
                            <p className="text-sm text-gray-500 mb-2">{m.date}</p>
                            <p>{m.description}</p>
                            {m.image && (
                                <img
                                    src={`http://localhost:5001/static/uploads/${m.image}`}
                                    alt="milestone"
                                    className="mt-3 rounded w-40"
                                />
                            )}
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}
