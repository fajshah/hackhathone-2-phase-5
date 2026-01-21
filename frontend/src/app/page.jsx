
"use client";

import Chatbot from "./components/Chatbot";

export default function Page() {
  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        backgroundColor: "#d48fc9",
        padding: "20px",
      }}
    >
      <div
        style={{
          textAlign: "center",
          backgroundColor: "white",
          padding: "30px",
          borderRadius: "10px",
          boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)",
        }}
      >
        <h1
          style={{
            color: "#333",
            marginBottom: "20px",
            fontSize: "24px",
          }}
        >
          HELLO WORLD — REACT IS WORKING
        </h1>

        <Chatbot />
      </div>
    </div>
  );
}
