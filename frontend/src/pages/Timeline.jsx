import { VerticalTimeline, VerticalTimelineElement } from 'react-vertical-timeline-component';
import 'react-vertical-timeline-component/style.min.css';
import { FaBaby, FaCamera } from 'react-icons/fa';
import { useEffect, useState } from 'react';
import axios from 'axios';
import { Link } from "react-router-dom";

export default function Timeline() {
    const [milestones, setMilestones] = useState([]);
    const user_id = localStorage.getItem("user_id");

    useEffect(() => {
        axios.get(`/api/milestones?user_id=${user_id}`).then((res) => {
            // sortera efter datum stigande
            const sorted = [...res.data].sort((a, b) => new Date(a.date) - new Date(b.date));
            setMilestones(sorted);
        });
    }, []);

    return (
        <div className="min-h-screen bg-pink-50 p-8">
            <h1 className="text-3xl text-pink-700 font-bold text-center mb-8">Min Tidslinje 🍼</h1>
            <div className="flex justify-center mb-8">
                <Link
                    to="/milestones"
                    className="bg-white text-pink-700 border border-pink-400 px-4 py-2 rounded hover:bg-pink-50 transition"
                >
                    ← Tillbaka
                </Link>
            </div>
            <VerticalTimeline>
                {milestones.map((m) => (
                    <VerticalTimelineElement
                        key={m.id}
                        date={m.date}
                        iconStyle={{ background: '#ec4899', color: '#fff' }}
                        icon={m.image ? <FaCamera /> : <FaBaby />}
                    >
                        <h3 className="text-xl font-bold">{m.title}</h3>
                        <p>{m.description}</p>
                        {m.image && (
                            <img
                                src={`http://localhost:5001/static/uploads/${m.image}`}
                                alt="milestone"
                                className="mt-3 rounded-lg w-48"
                            />
                        )}
                    </VerticalTimelineElement>
                ))}
            </VerticalTimeline>
        </div>
    );
}
