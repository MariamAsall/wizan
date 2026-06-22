import { useState, useRef } from "react";
import { useTranslation } from "react-i18next";
import { UploadCloud, FileText, Trash2, Loader2, CheckCircle, XCircle } from "lucide-react";
import api from "../api/axios";

async function uploadFile(file) {
  const form = new FormData();
  form.append("file", file);
  const { data } = await api.post("/documents/", form);
  return data;
}

async function pollStatus(id) {
  const { data } = await api.get(`/documents/${id}/`);
  return data.status;
}

async function deleteFile(id) {
  await api.delete(`/documents/${id}/`);
}

function StatusBadge({ status }) {
  if (status === "processing") return <span className="flex items-center gap-1 rounded-full border border-yellow-200 bg-yellow-50 px-2 py-0.5 text-xs font-medium text-yellow-700"><Loader2 size={11} className="animate-spin" /> Processing</span>;
  if (status === "ready") return <span className="flex items-center gap-1 rounded-full border border-green-200  bg-green-50  px-2 py-0.5 text-xs font-medium text-green-700" ><CheckCircle size={11} /> Ready</span>;
  if (status === "failed") return <span className="flex items-center gap-1 rounded-full border border-red-200    bg-red-50    px-2 py-0.5 text-xs font-medium text-red-700"  ><XCircle size={11} /> Failed</span>;
}

export default function DocumentsPage() {
  const { t, i18n } = useTranslation();
  const dir = i18n.dir();
  const inputRef = useRef(null);
  const [docs, setDocs] = useState([]);
  const [dragging, setDragging] = useState(false);

  const updateDoc = (id, changes) =>
    setDocs((prev) => prev.map((d) => (d.id === id ? { ...d, ...changes } : d)));

  const handleUpload = async (files) => {
    const allFiles = Array.from(files);
    if (!allFiles.length) return;

    for (const file of allFiles) {
      // show the file immediately as processing
      const tempId = crypto.randomUUID();
      setDocs((prev) => [...prev, { id: tempId, filename: file.name, status: "processing" }]);

      // upload → get real id back
      const uploaded = await uploadFile(file);
      updateDoc(tempId, { id: uploaded.id });

      // poll until done
      const status = await pollStatus(uploaded.id);
      updateDoc(uploaded.id, { status });
    }
  };

  const handleDelete = async (id) => {
    await deleteFile(id);
    setDocs((prev) => prev.filter((d) => d.id !== id));
  };

  return (
    <div dir={dir} className="flex h-full flex-col">

      <header className="border-b border-border px-6 py-4">
        <h1 className="text-2xl mb-2 font-semibold text-foreground">{t("documents.title")}</h1>
        <p className="text-xs text-foreground/70">{t("documents.subtitle")}</p>
      </header>

      <div className="flex-1 space-y-4 overflow-y-auto p-6">

        {/* drop zone */}
        <div
          onClick={() => inputRef.current.click()}
          onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={(e) => { e.preventDefault(); setDragging(false); handleUpload(e.dataTransfer.files); }}
          className={`flex cursor-pointer flex-col items-center gap-3 rounded-2xl border-2 border-dashed p-20 text-center transition ${dragging ? "border-primary bg-primary/5" : "border-border bg-card hover:border-primary/50 hover:bg-primary/5"}`}
        >
          <UploadCloud size={32} className="text-foreground/30" />
          <p className="text-sm font-medium text-foreground">{t("documents.dropzone")}</p>
          <p className="text-xs text-foreground/50">{t("documents.allFiles")}</p>
          <input ref={inputRef} type="file" multiple className="hidden" onChange={(e) => handleUpload(e.target.files)} />
        </div>

        {/* file list */}
        {docs.map((doc) => (
          <div key={doc.id} className="flex items-center gap-3 rounded-xl border border-border bg-card px-4 py-3">
            <FileText size={18} className="shrink-0 text-foreground/40" />
            <span className="flex-1 truncate text-sm text-foreground">{doc.filename}</span>
            <StatusBadge status={doc.status} />
            <button
              onClick={() => handleDelete(doc.id)}
              disabled={doc.status === "processing"}
              className="ms-2 rounded-lg p-1.5 text-foreground/30 transition hover:bg-destructive hover:text-destructive-foreground disabled:cursor-not-allowed disabled:opacity-30"
            >
              <Trash2 size={15} />
            </button>
          </div>
        ))}

        {/* empty state */}
        {docs.length === 0 && (
          <p className="text-center text-sm text-foreground/40">{t("documents.empty")}</p>
        )}

      </div>
    </div>
  );
}