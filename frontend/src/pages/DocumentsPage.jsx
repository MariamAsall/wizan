import { useState, useRef, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { UploadCloud, FileText, Trash2, Loader2, CheckCircle, XCircle, AlertCircle } from "lucide-react";
import api from "../api/axios";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {AlertDialog,AlertDialogAction,AlertDialogCancel,AlertDialogContent,AlertDialogDescription,AlertDialogFooter,AlertDialogHeader,AlertDialogTitle,AlertDialogTrigger,
} from "@/components/ui/alert-dialog";

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
  if (status === "ready") return <span className="flex items-center gap-1 rounded-full border border-green-200  bg-green-50  px-2 py-0.5 text-xs font-medium text-green-700"><CheckCircle size={11} /> Ready</span>;
  if (status === "failed") return <span className="flex items-center gap-1 rounded-full border border-red-200    bg-red-50    px-2 py-0.5 text-xs font-medium text-red-700"><XCircle size={11} /> Failed</span>;
}

export default function DocumentsPage() {
  const { t, i18n } = useTranslation();
  const dir = i18n.dir();
  const inputRef = useRef(null);

  const [docs, setDocs] = useState([]);
  const [dragging, setDragging] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.get("/documents/").then(({ data }) => setDocs(data));
  }, []);

  const updateDoc = (id, changes) =>
    setDocs((prev) => prev.map((d) => (d.id === id ? { ...d, ...changes } : d)));

  const handleUpload = async (files) => {
    const pdfs = Array.from(files).filter((f) => f.type === "application/pdf");
    if (!pdfs.length) return;
    setError(null);

    for (const file of pdfs) {
      const tempId = crypto.randomUUID();
      setDocs((prev) => [...prev, { id: tempId, filename: file.name, status: "processing" }]);

      try {
        const uploaded = await uploadFile(file);
        updateDoc(tempId, { id: uploaded.id });

        const status = await pollStatus(uploaded.id);
        updateDoc(uploaded.id, { status });
      } catch (err) {
        setDocs((prev) => prev.filter((d) => d.id !== tempId));
        setError(t("documents.uploadError"));
      }
    }
  };

  const handleDelete = async (id) => {
    try {
      await deleteFile(id);
      setDocs((prev) => prev.filter((d) => d.id !== id));
    } catch (err) {
      setError(t("documents.deleteError"));
    }
  };

  return (
    <div dir={dir} className="flex h-full flex-col">

      <header className="border-b border-border px-6 py-4">
        <h1 className="text-2xl mb-2 font-semibold text-foreground">{t("documents.title")}</h1>
        <p className="text-xs text-foreground/70">{t("documents.subtitle")}</p>
      </header>

      <div className="flex-1 space-y-4 overflow-y-auto p-6">

        {/* error alert */}
        {error && (
          <Alert variant="destructive">
            <AlertCircle size={16} />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

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
          <p className="text-xs text-foreground/50">{t("documents.pdfs")}</p>
          <input ref={inputRef} type="file" accept=".pdf" multiple className="hidden" onChange={(e) => handleUpload(e.target.files)} />
        </div>

        {/* file list */}
        {docs.map((doc) => (
          <div key={doc.id} className="flex items-center gap-3 rounded-xl border border-border bg-card px-4 py-3">
            <FileText size={18} className="shrink-0 text-foreground/40" />
            <span className="flex-1 truncate text-sm text-foreground">{doc.filename}</span>
            <StatusBadge status={doc.status} />

            <AlertDialog>
              <AlertDialogTrigger asChild>
                <Button variant="destructive" disabled={doc.status === "processing"}>
                  <Trash2 size={15} />
                </Button>
              </AlertDialogTrigger>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>{t("documents.deleteTitle")}</AlertDialogTitle>
                  <AlertDialogDescription>
                    {t("documents.deleteMessage", { filename: doc.filename })}
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>{t("documents.cancel")}</AlertDialogCancel>
                  <AlertDialogAction onClick={() => handleDelete(doc.id)}>
                    {t("documents.confirm")}
                  </AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>

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