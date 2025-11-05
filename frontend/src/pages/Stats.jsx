import { useEffect, useState } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from 'recharts';
import { Link } from "react-router-dom";

export default function Stats() {
    const [data, setData] = useState([]);
    const user_id = localStorage.getItem("user_id");

    useEffect(() => {
        axios.get(`/api/milestones?user_id=${user_id}`).then((res) => {
            const monthly = {};
            res.data.forEach((m) => {
                const month = new Date(m.date).toLocaleString("sv-SE", { month: "short", year: "numeric" });
                monthly[month] = (monthly[month] || 0) + 1;
            });
            const chartData = Object.entries(monthly).map(([month, count]) => ({ month, count }));
            setData(chartData);
        });
    }, []);

    return (
        <div className="min-h-screen bg-pink-50 p-8">
            <h1 className="text-3xl text-pink-700 font-bold text-center mb-8">Statistik 📊</h1>
            <div className="flex justify-center mb-8">
                            <Link
                                to="/milestones"
                                className="bg-white text-pink-700 border border-pink-400 px-4 py-2 rounded hover:bg-pink-50 transition"
                            >
                                ← Tillbaka
                            </Link>
                        </div>
            <div className="bg-white p-6 rounded-2xl shadow max-w-3xl mx-auto">
                <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={data}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="month" />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="count" fill="#ec4899" />
                    </BarChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
}
