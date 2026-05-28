import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer
} from "recharts"

import { useState } from "react"
import axios from "axios"
import jsPDF from "jspdf"

function App() {

  const [file, setFile] = useState(null)
  const [jobDescription, setJobDescription] = useState("")
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [darkMode, setDarkMode] = useState(true)

  // Chart Data
  const chartData = [

    {
      name: "ATS Score",
      value: data ? data.ats_score : 0
    },

    {
      name: "Remaining",
      value: data ? 100 - data.ats_score : 100
    }
  ]

  // Chart Colors
  const COLORS = ["#06b6d4", "#1e293b"]

  // Upload Resume
  const handleUpload = async () => {

    if (!file) {

      alert("Please Upload Resume")
      return
    }

    const formData = new FormData()

    formData.append("file", file)
    formData.append("job_description", jobDescription)

    try {

      setLoading(true)

      const response = await axios.post(
        "http://127.0.0.1:8000/upload",
        formData
      )

      setData(response.data)

    } catch (error) {

      console.log(error)

      alert("Upload Failed")

    } finally {

      setLoading(false)
    }
  }

  // Download PDF
  const downloadPDF = () => {

    const doc = new jsPDF()

    doc.setFontSize(22)

    doc.text("AI Resume Analysis Report", 20, 20)

    doc.setFontSize(14)

    doc.text(
      `ATS Score: ${data.ats_score}%`,
      20,
      40
    )

    doc.text(
      `Job Match Score: ${data.job_match_score}%`,
      20,
      55
    )

    doc.text(
      `Found Skills: ${data.found_skills.join(", ")}`,
      20,
      70
    )

    doc.text(
      `Missing Skills: ${data.missing_skills.join(", ")}`,
      20,
      85
    )

    doc.text(
      "AI Feedback:",
      20,
      105
    )

    const splitText = doc.splitTextToSize(
      data.ai_feedback,
      170
    )

    doc.text(
      splitText,
      20,
      120
    )

    doc.save("AI_Resume_Report.pdf")
  }

  return (

    <div className={`

      ${
        darkMode
          ? "bg-gradient-to-br from-black via-[#020617] to-[#001233] text-white"
          : "bg-gray-100 text-black"
      }

      min-h-screen transition-all duration-500

    `}>

      {/* Navbar */}
      <nav className="flex justify-between items-center px-10 py-6 border-b border-cyan-500">

        <h1 className="text-3xl font-bold text-cyan-400">

          AI Resume Analyzer 🚀

        </h1>

        <div className="flex gap-6 text-lg items-center">

          <a
            href="#"
            className="hover:text-cyan-400 transition"
          >
            Home
          </a>

          <a
            href="#"
            className="hover:text-cyan-400 transition"
          >
            Features
          </a>

          <a
            href="#"
            className="hover:text-cyan-400 transition"
          >
            About
          </a>

          <a
            href="#"
            className="hover:text-cyan-400 transition"
          >
            Contact
          </a>

          {/* Dark Mode Button */}
          <button
            onClick={() => setDarkMode(!darkMode)}
            className="bg-cyan-500 hover:bg-cyan-600 px-5 py-2 rounded-xl font-bold"
          >

            {
              darkMode
                ? "☀️ Light"
                : "🌙 Dark"
            }

          </button>

        </div>

      </nav>

      {/* Hero Section */}
      <section className="flex flex-col items-center justify-center text-center py-24 px-5">

        <h1 className="text-6xl md:text-7xl font-extrabold leading-tight">

          Analyze Your Resume <br />

          <span className="text-cyan-400">

            Using AI

          </span>

        </h1>

        <p className="text-gray-400 mt-8 max-w-2xl text-xl leading-8">

          Get ATS score, AI feedback,
          skill analysis, interview tips,
          and job match reports instantly.

        </p>

      </section>

      {/* Upload Section */}
      <section className="flex justify-center px-5 pb-20">

        <div className={`

          ${
            darkMode
              ? "bg-[#081226]"
              : "bg-white"
          }

          shadow-[0_0_30px_#06b6d4]
          border border-cyan-500
          rounded-3xl
          p-10
          w-full
          max-w-3xl

        `}>

          <h2 className="text-4xl font-bold text-center mb-10 text-cyan-400">

            Upload Resume

          </h2>

          {/* File Upload */}
          <input
            type="file"
            accept=".pdf"
            id="resumeUpload"
            className="hidden"
            onChange={(e) => setFile(e.target.files[0])}
          />

          {/* Upload Box */}
          <label
            htmlFor="resumeUpload"
            className="cursor-pointer block border-2 border-dashed border-cyan-500 rounded-2xl p-10 text-center hover:bg-cyan-500/10 transition duration-300"
          >

            <div className="text-6xl mb-4">

              📄

            </div>

            <p className="text-2xl font-semibold">

              Click to Upload Resume

            </p>

            <p className="text-gray-400 mt-2">

              PDF files only

            </p>

            {
              file && (

                <p className="mt-5 text-cyan-400 font-bold">

                  {file.name}

                </p>

              )
            }

          </label>

          {/* Job Description */}
          <textarea
            placeholder="Paste Job Description Here..."
            className={`

              w-full
              mt-8
              border border-cyan-500
              rounded-2xl
              p-5
              h-40
              outline-none

              ${
                darkMode
                  ? "bg-black text-white"
                  : "bg-gray-100 text-black"
              }

            `}
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
          />

          {/* Analyze Button */}
          <button
            onClick={handleUpload}
            className="w-full mt-8 bg-cyan-500 hover:bg-cyan-600 py-4 rounded-2xl text-xl font-bold transition-all duration-300"
          >

            {
              loading
                ? "⚡ AI Analyzing Resume..."
                : "🚀 Analyze Resume"
            }

          </button>

        </div>

      </section>

      {/* Results */}
      {
        data && (

          <section className="px-5 pb-20">

            {/* Top Cards */}
            <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">

              {/* ATS Score */}
              <div className="bg-[#081226] shadow-[0_0_30px_#06b6d4] border border-cyan-500 rounded-3xl p-8">

                <h2 className="text-3xl font-bold text-cyan-400 mb-8 text-center">

                  ATS Score

                </h2>

                <div className="flex justify-center">

                  <div className="relative w-52 h-52">

                    <svg className="w-52 h-52 transform -rotate-90">

                      {/* Background */}
                      <circle
                        cx="104"
                        cy="104"
                        r="85"
                        stroke="#1e293b"
                        strokeWidth="15"
                        fill="transparent"
                      />

                      {/* Progress */}
                      <circle
                        cx="104"
                        cy="104"
                        r="85"
                        stroke="#06b6d4"
                        strokeWidth="15"
                        fill="transparent"
                        strokeDasharray={534}
                        strokeDashoffset={
                          534 - (534 * data.ats_score) / 100
                        }
                        strokeLinecap="round"
                      />

                    </svg>

                    <div className="absolute inset-0 flex items-center justify-center">

                      <span className="text-5xl font-bold text-cyan-400">

                        {data.ats_score}%

                      </span>

                    </div>

                  </div>

                </div>

              </div>

              {/* Job Match */}
              <div className="bg-[#081226] shadow-[0_0_30px_#22c55e] border border-green-500 rounded-3xl p-8">

                <h2 className="text-3xl font-bold text-green-400 mb-8 text-center">

                  Job Match Score

                </h2>

                <div className="flex items-center justify-center h-[220px]">

                  <span className="text-7xl font-bold text-green-400">

                    {data.job_match_score}%

                  </span>

                </div>

              </div>

              {/* Found Skills */}
              <div className="bg-[#081226] shadow-[0_0_30px_#06b6d4] border border-cyan-500 rounded-3xl p-8">

                <h2 className="text-3xl font-bold text-cyan-400 mb-5">

                  Found Skills

                </h2>

                <div className="flex flex-wrap gap-3">

                  {
                    data.found_skills.map((skill, index) => (

                      <span
                        key={index}
                        className="bg-cyan-500 text-black font-bold px-4 py-2 rounded-xl"
                      >

                        {skill}

                      </span>

                    ))
                  }

                </div>

              </div>

              {/* Missing Skills */}
              <div className="bg-[#081226] shadow-[0_0_30px_#ef4444] border border-red-500 rounded-3xl p-8">

                <h2 className="text-3xl font-bold text-red-400 mb-5">

                  Missing Skills

                </h2>

                <div className="flex flex-wrap gap-3">

                  {
                    data.missing_skills.map((skill, index) => (

                      <span
                        key={index}
                        className="bg-red-500 text-white font-bold px-4 py-2 rounded-xl"
                      >

                        {skill}

                      </span>

                    ))
                  }

                </div>

              </div>

            </div>

            {/* Analytics */}
            <div className="max-w-5xl mx-auto mt-10 bg-[#081226] shadow-[0_0_30px_#06b6d4] border border-cyan-500 rounded-3xl p-10">

              <h2 className="text-4xl font-bold text-cyan-400 mb-10">

                📊 Analytics Dashboard

              </h2>

              <div className="h-[400px]">

                <ResponsiveContainer width="100%" height="100%">

                  <PieChart>

                    <Pie
                      data={chartData}
                      cx="50%"
                      cy="50%"
                      innerRadius={90}
                      outerRadius={140}
                      paddingAngle={5}
                      dataKey="value"
                    >

                      {
                        chartData.map((entry, index) => (

                          <Cell
                            key={`cell-${index}`}
                            fill={COLORS[index % COLORS.length]}
                          />

                        ))
                      }

                    </Pie>

                    <Tooltip />

                  </PieChart>

                </ResponsiveContainer>

              </div>

            </div>

            {/* AI Feedback */}
            <div className="max-w-5xl mx-auto mt-10 bg-[#081226] shadow-[0_0_30px_#06b6d4] border border-cyan-500 rounded-3xl p-10">

              <div className="flex justify-between items-center mb-8">

                <h2 className="text-4xl font-bold text-cyan-400">

                  AI Resume Analysis

                </h2>

                <button
                  onClick={downloadPDF}
                  className="bg-green-500 hover:bg-green-600 px-6 py-3 rounded-2xl font-bold"
                >

                  📄 Download Report

                </button>

              </div>

              <div className="whitespace-pre-wrap text-gray-300 leading-8">

                {data.ai_feedback}

              </div>

            </div>

            {/* Interview Section */}
            <div className="max-w-5xl mx-auto mt-10 bg-[#081226] shadow-[0_0_30px_#eab308] border border-yellow-500 rounded-3xl p-10">

              <h2 className="text-4xl font-bold text-yellow-400 mb-8">

                🎯 AI Interview Preparation

              </h2>

              <div className="whitespace-pre-wrap text-gray-300 leading-8">

                {data.ai_feedback}

              </div>

            </div>

          </section>

        )
      }

    </div>
  )
}

export default App