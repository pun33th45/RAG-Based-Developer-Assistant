import { useState } from "react";
import Chat from "./components/Chat";
import Upload from "./components/Upload";

export default function App() {
  const [lastUpload, setLastUpload] = useState(null);

  return (
    <div className="min-h-screen bg-ink text-slate-100">
      <Upload onIndexed={setLastUpload} />
      <Chat indexedSummary={lastUpload} />
    </div>
  );
}
