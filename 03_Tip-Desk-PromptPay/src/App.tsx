import { useEffect, useState } from 'react'
import './App.css'

type Tip = {
  id: string
  name: string
  amount: number
  message: string
  status: 'pending' | 'confirmed'
  created_at: number
  confirmed_at?: number
  qr_data?: string
  promptpay_payload?: string
}

const API = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
const money = new Intl.NumberFormat('th-TH', { style: 'currency', currency: 'THB' })
const date = new Intl.DateTimeFormat('th-TH', { dateStyle: 'medium', timeStyle: 'short' })

function App() {
  const [form, setForm] = useState({ name: 'anonymous', amount: '', message: '' })
  const [activeTip, setActiveTip] = useState<Tip | null>(null)
  const [tips, setTips] = useState<Tip[]>([])
  const [screenMode, setScreenMode] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  function speakMessage(message: string) {
    if (!('speechSynthesis' in window)) return
    window.speechSynthesis.cancel()
    const speech = new SpeechSynthesisUtterance(message)
    speech.lang = 'th-TH'
    speech.rate = 0.92
    speech.pitch = 1.05
    window.speechSynthesis.speak(speech)
  }

  function openScreen() {
    setScreenMode(true)
    if (activeTip) speakMessage(activeTip.message || 'ขอบคุณที่แวะมานะ')
  }

  useEffect(() => {
    fetch(`${API}/api/tips`).then((response) => response.json()).then(setTips).catch(() => setError('เชื่อมต่อเซิร์ฟเวอร์ไม่ได้'))
    const source = new EventSource(`${API}/api/events`)
    source.addEventListener('tip', (event) => {
      const tip = JSON.parse((event as MessageEvent).data) as Tip
      setTips((current) => [tip, ...current.filter((item) => item.id !== tip.id)].slice(0, 50))
      setActiveTip(tip)
    })
    return () => source.close()
  }, [])

  useEffect(() => {
    const amount = Number(form.amount)
    if (!Number.isFinite(amount) || amount <= 0) {
      setActiveTip(null)
      return
    }
    const timer = window.setTimeout(async () => {
      setBusy(true)
      setError('')
      try {
        const response = await fetch(`${API}/api/tips`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ ...form, amount }) })
        const tip = await response.json()
        if (!response.ok) throw new Error(tip.detail ?? 'สร้าง QR ไม่สำเร็จ')
        setActiveTip(tip)
      } catch (reason) {
        setError(reason instanceof Error ? reason.message : 'เกิดข้อผิดพลาด')
      } finally {
        setBusy(false)
      }
    }, 350)
    return () => window.clearTimeout(timer)
  }, [form])

  return (
    <main className="app-shell">
      <header className="topbar"><div className="brand"><span className="brand-mark">+</span><span>tip desk</span></div><div className="connection"><span className="pulse" /> LIVE / พร้อมรับโดเนท</div></header>
      <section className="intro"><p className="eyebrow">A LITTLE LOVE, LIVE ON SCREEN</p><h1>แวะมาเติมพลัง<br /><em>ให้กันหน่อย</em></h1><p className="lede">ส่งทิปเล็ก ๆ พร้อมข้อความน่ารัก แล้วมาดูชื่อคุณเด้งขึ้นจอแบบสด ๆ กัน</p><button className="screen-button" type="button" onClick={openScreen}>เปิดจอรอเสียงเชียร์ <span>↗</span></button></section>
      <section className={`workspace ${activeTip?.qr_data ? 'has-qr' : ''}`}>
        <div className="create-panel panel"><div className="panel-heading"><span className="step">01</span><div><p className="eyebrow">YOUR LITTLE SHOUT-OUT</p><h2>ฝากข้อความไว้ตรงนี้</h2></div></div><form onSubmit={(event) => event.preventDefault()}><label>ชื่อของคุณ <input value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} placeholder="anonymous" /></label><label>อยากส่งกำลังใจกี่บาท <div className="amount-input"><input required min="1" step="0.01" type="number" value={form.amount} onChange={(event) => setForm({ ...form, amount: event.target.value })} /><span>THB</span></div></label><label>พิมพ์อะไรฝากไว้บนจอ <textarea maxLength={240} value={form.message} onChange={(event) => setForm({ ...form, message: event.target.value })} placeholder="วันนี้ทำได้ดีมาก! สู้ ๆ นะ" rows={4} /></label><p className="auto-status">{busy ? 'กำลังเตรียมเซอร์ไพรส์...' : 'ใส่ยอดปุ๊บ QR เด้งให้ปั๊บ'}</p>{error && <p className="error">{error}</p>}</form></div>
        <div className={`qr-panel panel qr-panel-shell ${activeTip?.qr_data ? 'qr-ready' : ''}`}><div className="panel-heading"><span className="step">02</span><div><p className="eyebrow">SCAN TO SUPPORT</p><h2>การ์ดรับโดเนท</h2></div></div><div className="qr-slide-card">{activeTip?.qr_data ? <><img src={activeTip.qr_data} alt="QR พร้อมเพย์สำหรับรายการโดเนท" /><strong>{money.format(activeTip.amount)}</strong><small>{activeTip.name || 'anonymous'} · พร้อมเพย์</small></> : <><span className="qr-cover-mark">QR</span><small>{busy ? 'กำลังสร้าง QR...' : 'ใส่จำนวนเงินเพื่อแสดง QR'}</small></>}</div><p className="hint">QR จะเลื่อนออกมาอัตโนมัติเมื่อใส่จำนวนเงิน</p></div>
      </section>
      <section className="history-section"><div className="section-title"><div><p className="eyebrow">RECENT ACTIVITY</p><h2>รายการล่าสุด</h2></div><span>{tips.filter((tip) => tip.status === 'confirmed').length} confirmed</span></div><div className="tip-list">{tips.length === 0 ? <p className="no-tips">ยังไม่มีรายการโดเนท</p> : tips.map((tip) => <article className={`tip-row ${tip.status}`} key={tip.id}><div className="avatar">{(tip.name || 'anonymous').slice(0, 1).toUpperCase()}</div><div className="tip-copy"><strong>{tip.name || 'anonymous'}</strong><p>{tip.message || 'สนับสนุนคุณ'}</p></div><time>{date.format(new Date(tip.created_at * 1000))}</time><b>{money.format(tip.amount)}</b><span className="status">{tip.status === 'confirmed' ? 'ได้รับแล้ว' : 'รอชำระ'}</span></article>)}</div></section>
      {screenMode && <div className="overlay"><button className="close-button" type="button" onClick={() => { setScreenMode(false); window.speechSynthesis.cancel() }}>ปิดหน้าจอ ×</button><div className="stream-card"><p className="eyebrow">NEW SUPPORT</p>{activeTip ? <><div className="stream-amount">{money.format(activeTip.amount)}</div><h2>{activeTip.name || 'anonymous'} <span>{activeTip.message || 'ขอบคุณที่แวะมานะ!'}</span></h2></> : <><div className="stream-icon">+</div><h2>รอข้อความโดเนท</h2><p className="stream-message">ข้อความจากผู้สนับสนุนจะปรากฏที่นี่</p></>}</div></div>}
    </main>
  )
}

export default App
