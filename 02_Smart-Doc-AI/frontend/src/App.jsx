import React, { useState, useEffect } from 'react';
const IconSearch = () => <svg width="24" h="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8" /><path d="m21 21-4.3-4.3" /></svg>;
const IconTranslate = () => <svg width="24" h="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m5 8 6 6" /><path d="m4 14 6-6" /><path d="M2 5h12" /><path d="M7 2h1" /><path d="m22 22-5-10-5 10" /><path d="M14 18h6" /></svg>;
const IconWiki = () => <svg width="24" h="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M16 16v1a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2h2" /><path d="M21 14V3a2 2 0 0 0-2-2H10a2 2 0 0 0-2 2v5" /><path d="M13 10V3" /><path d="M11 20h2" /></svg>;
const IconWeb = () => <svg width="24" h="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10" /><path d="M12 2a14.5 14.5 0 0 0 0 20" /><path d="M2 12h20" /></svg>;
const IconMicroscope = () => <svg width="24" h="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M6 18h8" /><path d="M3 22h18" /><path d="M14 22a7 7 0 1 0-14 0" /><path d="M9 14a7 7 0 0 0 2-13.85" /><path d="M21 2v10" /><path d="m17 10 4 4 4-4" /></svg>;
const IconFile = () => <svg width="24" h="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" /><polyline points="14 2 14 8 20 8" /></svg>;
const IconDownload = () => <svg width="24" h="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v4" /><polyline points="7 10 12 15 17 10" /><line x1="12" y1="15" x2="12" y2="3" /></svg>;
function App() {
  const [topic, setTopic] = useState('');
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);
  const [seconds, setSeconds] = useState(0);
  const [activeStep, setActiveStep] = useState(0);
  const [fileUrl, setFileUrl] = useState(null);
  const steps = [
    { label: "วิเคราะห์คำค้นหา", icon: <IconTranslate />, desc: "กำลังแปลภาษาและหาคำที่เกี่ยวข้อง" },
    { label: "Wikipedia", icon: <IconWiki />, desc: "ดึงข้อมูลจากสารานุกรมทั่วโลก" },
    { label: "ค้นหาเว็บไซต์", icon: <IconWeb />, desc: "รวบรวมบทความและข่าวสาร" },
    { label: "ค้นหางานวิจัย", icon: <IconMicroscope />, desc: "ดึงบทคัดย่อจาก ArXiv Global" },
    { label: "สร้างเอกสาร", icon: <IconFile />, desc: "รวบรวมเนื้อหาและไฮไลต์ที่มา" }
  ];
  useEffect(() => {
    let timer;
    if (loading) {
      timer = setInterval(() => {
        setSeconds(s => s + 1);
        if (seconds % 8 === 0 && activeStep < steps.length - 1) {
          setActiveStep(prev => prev + 1);
        }
      }, 1000);
    } else {
      setSeconds(0);
      setActiveStep(0);
      clearInterval(timer);
    }
    return () => clearInterval(timer);
  }, [loading, seconds, activeStep]);
  const handleScout = async () => {
    if (!topic) return alert("กรุณาใส่หัวข้อ");
    setLoading(true);
    setDone(false);
    try {
      const formData = new FormData();
      formData.append('topic', topic);
      formData.append('page_count', 50);
      const response = await fetch('/scout-to-word', {
        method: 'POST',
        body: formData,
      });
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      setFileUrl(url);
      setTimeout(() => {
        setLoading(false);
        setDone(true);
      }, 1500);
    } catch (error) {
      alert("error unicorn");
      setLoading(false);
    }
  };
  return (
    <div className="min-h-screen bg-[#FBFBFD] flex items-center justify-center p-6 font-sans overflow-hidden text-[#1D1D1F]">
      <div className="relative flex items-center justify-center w-full max-w-5xl h-[650px]">
        {/* กล่องหลัก: Harvester Card (Minimal) */}
        <div className={`z-20 w-full max-w-md bg-white/90 backdrop-blur-3xl rounded-[2rem] shadow-[0_30px_60px_rgba(0,0,0,0.05)] border border-white/50 p-12 transition-all duration-1000 ease-[cubic-bezier(0.4,0,0.2,1)] ${loading || done ? '-translate-x-56 rotate-[-2deg] scale-95' : 'translate-x-0'}`}>
          <header className="text-center mb-12">
            {/* โลโก้ Premium Finder ✨🔍 (เรียบหรู) */}
            <div className="relative w-20 h-20 rounded-3xl flex items-center justify-center mx-auto mb-5 transition-all duration-500 bg-[#0071E3] text-white shadow-lg shadow-blue-100">
              <span className="text-2xl opacity-80">✨</span>
              <div className="absolute inset-0 flex items-center justify-center transform translate-x-1 translate-y-1">
                <IconSearch />
              </div>
            </div>
            <h1 className="text-3xl font-bold tracking-tight">Harvester</h1>
            <p className="text-[12px] text-[#86868B] font-semibold mt-1 uppercase tracking-[0.2em]">Experimental</p>
          </header>
          {!loading && !done ? (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-3 duration-500">
              <input
                type="text" value={topic} onChange={(e) => setTopic(e.target.value)}
                placeholder="Cyber Security, AI, DevOps..."
                className="w-full p-5 bg-[#F5F5F7] rounded-2xl outline-none focus:ring-4 focus:ring-blue-100 font-medium text-lg transition-all border border-transparent focus:border-blue-200"
              />
              <button onClick={handleScout} className="w-full bg-[#0071E3] text-white py-5 rounded-2xl font-bold text-lg hover:bg-[#0077ED] active:scale-95 transition-all shadow-md shadow-blue-100">
                Start Scoping
              </button>
            </div>
          ) : done ? (
            <div className="text-center space-y-6 animate-in fade-in duration-700">
              {/* Premium Checkmark ✅ (วงกลมสีเขียวนุ่มนวล) */}
              <div className="w-16 h-16 bg-[#E3F9F1] text-[#00A67E] rounded-full flex items-center justify-center mx-auto mb-4 animate-checkmark">
                <svg width="32" h="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12" /></svg>
              </div>
              <p className="text-[#86868B] font-medium text-lg">รวบรวมข้อมูลเรื่อง <br /><span className="text-[#1D1D1F] font-bold">"{topic}"</span> เรียบร้อย!</p>
              <button onClick={() => { setDone(false); setTopic(''); }} className="px-8 py-3 bg-[#F5F5F7] rounded-2xl text-sm font-bold text-[#0071E3] hover:bg-blue-50 transition-all">
                Search Again
              </button>
            </div>
          ) : null}
        </div>
        {/* แผงแอนิเมชั่นโหลด (Premium Loading Panel) */}
        <div className={`absolute z-15 w-80 h-[480px] bg-white rounded-[2.5rem] shadow-[0_20px_50px_rgba(0,0,0,0.06)] border border-gray-100 p-10 flex flex-col transition-all duration-1000 ease-[cubic-bezier(0.175,0.885,0.32,1.275)] ${loading ? 'translate-x-56 opacity-100 rotate-[4deg] scale-100' : 'translate-x-0 opacity-0 scale-75 pointer-events-none'}`}>
          <div className="flex-1 overflow-hidden space-y-8">
            <div className="flex items-center space-x-3.5 mb-8">
              <div className="w-12 h-12 bg-[#F5F5F7] text-[#0071E3] rounded-2xl flex items-center justify-center border border-gray-100 animate-pulse">
                <IconDownload />
              </div>
              <div>
                <h4 className="text-sm font-bold truncate w-44">{topic || "Data Stream"}</h4>
                <p className="text-[10px] text-[#0071E3] font-bold tracking-widest uppercase">Harvesting...</p>
              </div>
            </div>

            <div className="text-center">
              <h3 className="text-lg font-bold tracking-tight text-[#1D1D1F]">{steps[activeStep].label}</h3>
              <p className="text-xs text-[#86868B] mt-2 italic font-medium">"{steps[activeStep].desc}"</p>
            </div>
            {/* Premium Data Flow Progress */}
            <div className="flex justify-center items-center relative h-10 px-2 mt-4">
              <div className="absolute top-1/2 left-0 w-full h-1 bg-[#F5F5F7] -translate-y-1/2 z-0 rounded-full"></div>
              <div className="absolute top-1/2 left-0 h-1 bg-[#0071E3] -translate-y-1/2 z-0 rounded-full transition-all duration-1000" style={{ width: `${(activeStep / (steps.length - 1)) * 100}%` }}></div>
              <div className="absolute top-1/2 left-0 h-1 animate-data-flow -translate-y-1/2 z-0 rounded-full" style={{ width: `${(activeStep / (steps.length - 1)) * 100}%` }}></div>
              {steps.map((step, i) => (
                <div key={i} className="relative z-10 flex flex-col items-center flex-1">
                  <div className={`w-9 h-9 rounded-full flex items-center justify-center transition-all duration-700 ${i <= activeStep ? 'bg-[#0071E3] text-white shadow-md shadow-blue-100' : 'bg-white border border-[#F5F5F7] text-[#D2D2D7]'}`}>
                    <div className="scale-75">{i < activeStep ? <svg width="24" h="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3"><polyline points="20 6 9 17 4 12" /></svg> : step.icon}</div>
                  </div>
                </div>
              ))}
            </div>
            <div className="text-center bg-[#F5F5F7] py-3.5 rounded-2xl mt-8">
              <p className="text-xs font-mono font-bold text-[#86868B] uppercase tracking-widest">
                Elapsed Time • {Math.floor(seconds / 60)}:{(seconds % 60).toString().padStart(2, '0')}
              </p>
            </div>
          </div>
        </div>
        {/* เอกสารเด้ง (Premium DOCX Card) */}
        <div className={`absolute z-10 w-80 h-[550px] bg-white rounded-[2.5rem] shadow-[0_30px_70px_rgba(0,0,0,0.1)] border border-gray-100 p-10 flex flex-col transition-all duration-1000 ease-[cubic-bezier(0.175,0.885,0.32,1.275)] ${done ? 'translate-x-60 opacity-100 rotate-[5deg] scale-100' : 'translate-x-0 opacity-0 scale-75 pointer-events-none'}`}>
          <div className="flex-1">
            <div className="w-16 h-16 bg-[#F5F5F7] text-[#1D1D1F] rounded-2xl flex items-center justify-center mb-6 shadow-inner border border-gray-100">
              <IconFile />
            </div>
            <h4 className="text-xl font-bold leading-tight mb-2 truncate text-[#1D1D1F]">{topic || "Research Result"}</h4>
            <p className="text-[11px] text-[#0071E3] font-bold tracking-widest uppercase mb-8">Ready for download</p>
            <div className="space-y-4">
              <div className="w-full h-2.5 bg-[#F5F5F7] rounded-full" />
              <div className="w-full h-2.5 bg-[#F5F5F7] rounded-full" />
              <div className="w-4/5 h-2.5 bg-[#F5F5F7] rounded-full" />
            </div>
            <div className="mt-10 p-6 bg-[#FBFBFD] rounded-[2rem] border border-gray-100">
              <p className="text-[12px] leading-relaxed text-[#86868B] italic font-medium">
                "เนื้อหาประกอบด้วย ข้อมูลจาก Wikipedia, งานวิจัย ArXiv และผลการค้นหาเว็บที่แปลเป็นไทยเรียบร้อยแล้ว"
              </p>
            </div>
          </div>
          <a href={fileUrl} download={`Harvester_${topic}.docx`} className="w-full bg-[#1D1D1F] text-white py-6 rounded-2xl font-bold text-center hover:bg-black transition-all shadow-2xl active:scale-95 flex items-center justify-center space-x-2">
            <IconDownload />
            <span>Download DOCX</span>
          </a>
        </div>
      </div>
      <style>{`
        @keyframes data-flow {
          0% { background-position: 0% 50%; }
          100% { background-position: 100% 50%; }
        }
        .animate-data-flow {
          background: linear-gradient(90deg, transparent 0%, rgba(0,113,227,0.3) 50%, transparent 100%);
          background-size: 200% 100%;
          animation: data-flow 1.5s linear infinite;
        }
        @keyframes checkmark {
          0% { transform: scale(0.5); opacity: 0; }
          60% { transform: scale(1.1); opacity: 1; }
          100% { transform: scale(1); opacity: 1; }
        }
        .animate-checkmark {
          animation: checkmark 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
        }
      `}</style>
    </div>
  );
}
export default App;