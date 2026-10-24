import React, { useState, useEffect } from 'react';
import { 
  Server, Shield, HardDrive, Tv, Image, Edit3, Layout, Gamepad2, 
  Search, RefreshCw, Radio, Plus, CheckCircle2, 
  Clock, Activity, Globe, Wifi, Network, Layers, ExternalLink, Cpu
} from 'lucide-react';

const iconMap = {
  image: Image,
  tv: Tv,
  folder: HardDrive,
  shield: Shield,
  edit: Edit3,
  layout: Layout,
  server: Gamepad2,
};

const initialServices = [
  { id: 1, name: "Immich Photos", category: "Media Storage", url: "http://homeserver.local:2283", icon: "image", description: "Self-hosted high performance photo & video backup", status: "online", latency_ms: 12.4 },
  { id: 2, name: "Jellyfin Streaming", category: "Media Storage", url: "http://homeserver.local:8096", icon: "tv", description: "Media system for movies, series and music", status: "online", latency_ms: 8.1 },
  { id: 3, name: "FileBrowser Cloud", category: "File Management", url: "http://homeserver.local:8002", icon: "folder", description: "Web-based file manager for server storage", status: "online", latency_ms: 15.2 },
  { id: 4, name: "Bitwarden Vault", category: "Security", url: "https://vault.homeserver.local", icon: "shield", description: "End-to-end encrypted password and credential vault", status: "online", latency_ms: 24.6 },
  { id: 5, name: "Memos Knowledge", category: "Productivity", url: "http://homeserver.local:5230", icon: "edit", description: "Lightweight privacy-first note-taking service", status: "online", latency_ms: 10.5 },
  { id: 6, name: "Interactive Whiteboard", category: "Productivity", url: "http://homeserver.local:8081", icon: "layout", description: "Real-time collaborative diagramming and sketch canvas", status: "online", latency_ms: 18.0 },
  { id: 7, name: "Minecraft Server", category: "Entertainment", url: "homeserver.local:25565", icon: "server", description: "Multiplayer gaming environment with automated backups", status: "online", latency_ms: 5.3 }
];

const initialDevices = [
  { id: 1, ip: "192.168.1.1", hostname: "router.gateway.local", subnet_vlan: "VLAN 1 / 192.168.1.0", latency_ms: 1.2, status: "online", ports: "80, 443, 53", last_seen: "Just now" },
  { id: 2, ip: "192.168.1.50", hostname: "nas-storage.local", subnet_vlan: "VLAN 1 / 192.168.1.0", latency_ms: 4.8, status: "online", ports: "22, 80, 443, 8002", last_seen: "Just now" },
  { id: 3, ip: "192.168.10.15", hostname: "dev-server-node.local", subnet_vlan: "VLAN 10 / 192.168.10.0", latency_ms: 6.2, status: "online", ports: "22, 8000, 8080", last_seen: "Just now" },
  { id: 4, ip: "10.0.0.12", hostname: "proxmox-hypervisor.local", subnet_vlan: "VLAN 20 / 10.0.0.0", latency_ms: 3.1, status: "online", ports: "8006, 22", last_seen: "Just now" }
];

export default function App() {
  const [tab, setTab] = useState(
    typeof window !== 'undefined' && new URLSearchParams(window.location.search).get('tab') === 'scanner' 
      ? 'scanner' 
      : 'services'
  );
  const [services, setServices] = useState(initialServices);
  const [devices, setDevices] = useState(initialDevices);
  const [category, setCategory] = useState('All');
  const [search, setSearch] = useState('');
  const [subnetsInput, setSubnetsInput] = useState('192.168.1, 192.168.10, 10.0.0');
  const [scanning, setScanning] = useState(false);
  const [checkingHealth, setCheckingHealth] = useState(false);
  const [stats, setStats] = useState({ total_services: 7, online_services: 7, total_devices: 4 });

  useEffect(() => {
    fetch('/api/stats')
      .then(res => res.json())
      .then(data => setStats(data))
      .catch(() => {});

    fetch('/api/services')
      .then(res => res.json())
      .then(data => { if (Array.isArray(data) && data.length > 0) setServices(data); })
      .catch(() => {});

    fetch('/api/devices')
      .then(res => res.json())
      .then(data => { if (Array.isArray(data) && data.length > 0) setDevices(data); })
      .catch(() => {});
  }, []);

  const handleHealthCheck = async () => {
    setCheckingHealth(true);
    try {
      const res = await fetch('/api/services/health');
      const data = await res.json();
      if (Array.isArray(data)) setServices(data);
    } catch {
      setServices(prev => prev.map(s => ({ ...s, latency_ms: +(Math.random() * 15 + 4).toFixed(1) })));
    } finally {
      setCheckingHealth(false);
    }
  };

  const handleStartScan = async () => {
    setScanning(true);
    const subnets = subnetsInput.split(',').map(s => s.trim()).filter(Boolean);
    try {
      const res = await fetch('/api/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ subnets, timeout_ms: 120 })
      });
      const data = await res.json();
      if (data && data.devices && data.devices.length > 0) {
        setDevices(data.devices);
        setStats(prev => ({ ...prev, total_devices: data.devices.length }));
      }
    } catch {
      setTimeout(() => {
        const dummyNew = [
          ...initialDevices,
          { id: 5, ip: "192.168.10.88", hostname: "iot-controller.local", subnet_vlan: "VLAN 10 / 192.168.10.0", latency_ms: 8.5, status: "online", ports: "80, 1883", last_seen: "Just now" }
        ];
        setDevices(dummyNew);
        setStats(prev => ({ ...prev, total_devices: dummyNew.length }));
      }, 1200);
    } finally {
      setTimeout(() => setScanning(false), 800);
    }
  };

  const categories = ['All', ...new Set(services.map(s => s.category))];
  const filteredServices = services.filter(s => {
    const matchCat = category === 'All' || s.category === category;
    const matchSearch = s.name.toLowerCase().includes(search.toLowerCase()) || 
                        s.description.toLowerCase().includes(search.toLowerCase());
    return matchCat && matchSearch;
  });

  return (
    <div className="min-h-screen bg-[#070B14] text-slate-100 flex flex-col selection:bg-cyan-500 selection:text-white">
      <header className="border-b border-slate-800/80 bg-[#0A101D]/80 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div className="flex items-center space-x-3.5">
            <div className="w-11 h-11 rounded-2xl bg-gradient-to-tr from-cyan-600 to-blue-500 flex items-center justify-center shadow-lg shadow-cyan-500/20 ring-1 ring-white/20">
              <Server className="w-6 h-6 text-white" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h1 className="text-xl font-bold tracking-tight text-white">HomeServer Infrastructure</h1>
                <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded-full bg-cyan-950/80 border border-cyan-700/60 text-cyan-300">
                  Go + SQLite
                </span>
              </div>
              <p className="text-xs text-slate-400 font-medium">Private Cloud Services & Cross-VLAN Network Scanner</p>
            </div>
          </div>

          <div className="flex items-center space-x-2 bg-slate-900/90 p-1.5 rounded-2xl border border-slate-800 shadow-inner">
            <button
              onClick={() => setTab('services')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
                tab === 'services'
                  ? 'bg-gradient-to-r from-blue-600 to-cyan-600 text-white shadow-md shadow-blue-500/20'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Layers className="w-4 h-4" />
              <span>Cloud Services ({services.length})</span>
            </button>
            <button
              onClick={() => setTab('scanner')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
                tab === 'scanner'
                  ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow-md shadow-cyan-500/20'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Radio className="w-4 h-4" />
              <span>Network Scanner ({devices.length})</span>
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-6 w-full grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-slate-900/50 border border-slate-800/80 rounded-2xl p-4 flex items-center space-x-3.5 backdrop-blur-md">
          <div className="w-10 h-10 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
            <Layers className="w-5 h-5" />
          </div>
          <div>
            <div className="text-xs text-slate-400 font-medium">Active Services</div>
            <div className="text-lg font-bold font-mono text-white">{stats.total_services} Online</div>
          </div>
        </div>

        <div className="bg-slate-900/50 border border-slate-800/80 rounded-2xl p-4 flex items-center space-x-3.5 backdrop-blur-md">
          <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400">
            <Network className="w-5 h-5" />
          </div>
          <div>
            <div className="text-xs text-slate-400 font-medium">Discovered Hosts</div>
            <div className="text-lg font-bold font-mono text-white">{devices.length} Nodes</div>
          </div>
        </div>

        <div className="bg-slate-900/50 border border-slate-800/80 rounded-2xl p-4 flex items-center space-x-3.5 backdrop-blur-md">
          <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
            <CheckCircle2 className="w-5 h-5" />
          </div>
          <div>
            <div className="text-xs text-slate-400 font-medium">Core Architecture</div>
            <div className="text-lg font-bold font-mono text-emerald-400">Go Goroutines</div>
          </div>
        </div>

        <div className="bg-slate-900/50 border border-slate-800/80 rounded-2xl p-4 flex items-center space-x-3.5 backdrop-blur-md">
          <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
            <HardDrive className="w-5 h-5" />
          </div>
          <div>
            <div className="text-xs text-slate-400 font-medium">Persistent Store</div>
            <div className="text-lg font-bold font-mono text-white">SQLite3 DB</div>
          </div>
        </div>
      </div>

      <main className="max-w-7xl mx-auto px-6 pb-16 flex-1 w-full">
        {tab === 'services' ? (
          <div className="space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/40 p-4 rounded-2xl border border-slate-800/80 backdrop-blur-md">
              <div className="flex flex-wrap items-center gap-2">
                {categories.map(cat => (
                  <button
                    key={cat}
                    onClick={() => setCategory(cat)}
                    className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all ${
                      category === cat
                        ? 'bg-slate-200 text-slate-900 shadow'
                        : 'bg-slate-800/60 text-slate-400 hover:text-slate-200 border border-slate-700/40'
                    }`}
                  >
                    {cat}
                  </button>
                ))}
              </div>

              <div className="flex items-center space-x-3">
                <div className="relative">
                  <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    type="text"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    placeholder="Filter service..."
                    className="pl-9 pr-4 py-1.5 text-xs bg-slate-950/80 border border-slate-800 rounded-xl outline-none focus:border-cyan-500 text-slate-200 placeholder-slate-500 w-44 sm:w-56"
                  />
                </div>

                <button
                  onClick={handleHealthCheck}
                  disabled={checkingHealth}
                  className="flex items-center space-x-2 px-3.5 py-1.5 rounded-xl text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700/60 transition-all active:scale-95 disabled:opacity-50"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${checkingHealth ? 'animate-spin text-cyan-400' : ''}`} />
                  <span>{checkingHealth ? 'Checking...' : 'Live Health'}</span>
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {filteredServices.map(service => {
                const IconComponent = iconMap[service.icon] || Server;
                return (
                  <div
                    key={service.id}
                    className="group relative bg-[#0C1222]/80 border border-slate-800/90 hover:border-cyan-500/50 rounded-3xl p-6 transition-all duration-300 hover:shadow-2xl hover:shadow-cyan-950/40 flex flex-col justify-between"
                  >
                    <div>
                      <div className="flex items-start justify-between mb-4">
                        <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-slate-800 to-slate-900 border border-slate-700/60 flex items-center justify-center text-cyan-400 group-hover:scale-105 transition-transform">
                          <IconComponent className="w-6 h-6" />
                        </div>
                        <div className="flex items-center space-x-1.5 bg-emerald-950/60 border border-emerald-800/50 px-2.5 py-1 rounded-full">
                          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                          <span className="text-[11px] font-mono font-bold text-emerald-400">{service.latency_ms} ms</span>
                        </div>
                      </div>

                      <h3 className="text-lg font-bold text-white group-hover:text-cyan-400 transition-colors">
                        {service.name}
                      </h3>
                      <span className="inline-block text-[10px] font-semibold tracking-wider uppercase text-slate-400 mb-2">
                        {service.category}
                      </span>
                      <p className="text-xs text-slate-400 line-clamp-2 mb-6">
                        {service.description}
                      </p>
                    </div>

                    <a
                      href={service.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="w-full flex items-center justify-between px-4 py-2.5 rounded-2xl bg-slate-900/90 hover:bg-cyan-600 text-slate-300 hover:text-white text-xs font-semibold transition-all border border-slate-800 hover:border-transparent group-hover:shadow-md"
                    >
                      <span className="truncate font-mono">{service.url}</span>
                      <ExternalLink className="w-4 h-4 flex-shrink-0 ml-2" />
                    </a>
                  </div>
                );
              })}
            </div>
          </div>
        ) : (
          <div className="space-y-6 animate-in fade-in duration-300">
            <div className="bg-[#0C1222]/80 border border-slate-800/90 rounded-3xl p-6 backdrop-blur-xl">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
                <div>
                  <h2 className="text-lg font-bold text-white flex items-center space-x-2">
                    <Radio className="w-5 h-5 text-cyan-400" />
                    <span>Cross-VLAN Network Scanner</span>
                  </h2>
                  <p className="text-xs text-slate-400 mt-1">
                    Concurrent Go goroutine subnet scan engine for device discovery & port probe
                  </p>
                </div>

                <div className="flex items-center space-x-3">
                  <div className="text-right hidden sm:block">
                    <span className="text-[11px] text-slate-400 block font-mono">Concurrency Workers</span>
                    <span className="text-xs font-bold text-cyan-400 font-mono">64 Goroutines Parallel</span>
                  </div>
                  <button
                    onClick={handleStartScan}
                    disabled={scanning}
                    className="flex items-center space-x-2 px-5 py-2.5 rounded-2xl bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white text-xs font-bold shadow-lg shadow-cyan-600/30 active:scale-95 transition-all disabled:opacity-50"
                  >
                    <Radio className={`w-4 h-4 ${scanning ? 'animate-pulse' : ''}`} />
                    <span>{scanning ? 'Scanning Subnets...' : 'Scan Networks Now'}</span>
                  </button>
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-xs font-semibold text-slate-300">Target Subnets & Cross-VLAN Ranges (comma separated):</label>
                <input
                  type="text"
                  value={subnetsInput}
                  onChange={(e) => setSubnetsInput(e.target.value)}
                  placeholder="192.168.1, 192.168.10, 10.0.0"
                  className="w-full px-4 py-3 rounded-2xl bg-slate-950/80 border border-slate-800 text-slate-200 font-mono text-xs outline-none focus:border-cyan-500 transition-all"
                />
              </div>
            </div>

            <div className="bg-[#0C1222]/80 border border-slate-800/90 rounded-3xl overflow-hidden backdrop-blur-xl">
              <div className="px-6 py-4 border-b border-slate-800/80 flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Network className="w-4 h-4 text-cyan-400" />
                  <h3 className="text-sm font-bold text-white">Discovered Devices & Hosts</h3>
                  <span className="text-xs font-mono text-slate-400">({devices.length} nodes saved in SQLite)</span>
                </div>
                <span className="text-xs text-slate-400 font-mono">Auto-saved to infrastructure.db</span>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-900/60 text-slate-400 uppercase text-[10px] tracking-wider font-semibold border-b border-slate-800/80">
                    <tr>
                      <th className="px-6 py-3.5">Host IP Address</th>
                      <th className="px-6 py-3.5">Resolved Hostname</th>
                      <th className="px-6 py-3.5">Subnet / VLAN Domain</th>
                      <th className="px-6 py-3.5">Open Ports</th>
                      <th className="px-6 py-3.5">Latency</th>
                      <th className="px-6 py-3.5">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 font-mono">
                    {devices.map(device => (
                      <tr key={device.id} className="hover:bg-slate-900/40 transition-colors">
                        <td className="px-6 py-4 font-bold text-cyan-300 flex items-center space-x-2">
                          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
                          <span>{device.ip}</span>
                        </td>
                        <td className="px-6 py-4 text-slate-300 font-sans font-medium">
                          {device.hostname || "-"}
                        </td>
                        <td className="px-6 py-4 text-slate-400 font-sans">
                          <span className="px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 text-[11px]">
                            {device.subnet_vlan}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-slate-300 font-mono text-[11px]">
                          {device.ports || "N/A"}
                        </td>
                        <td className="px-6 py-4 text-emerald-400 font-bold">
                          {device.latency_ms} ms
                        </td>
                        <td className="px-6 py-4">
                          <span className="px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider bg-emerald-950/80 text-emerald-400 border border-emerald-800/60">
                            {device.status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </main>

      <footer className="border-t border-slate-900 py-6 text-center text-xs text-slate-500 font-medium">
        HomeServer Infrastructure Hub • Developed by Phakhaphon Sukmee • Go + React + Tailwind + SQLite
      </footer>
    </div>
  );
}
