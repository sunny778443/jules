"use client";

import React, { useState, useEffect, useRef } from "react";
import {
  Terminal, Cpu, Database, ToyBrick, FileCode, MessageSquarePlus,
  Send, Trash2, ShieldAlert, Volume2, Search, Play, HelpCircle,
  ExternalLink, Layers, RefreshCw, FolderOpen, Radio
} from "lucide-react";

export default function JarvisDashboard() {
  const [activeTab, setActiveTab] = useState<"chat" | "memory" | "plugins" | "files" | "stats">("chat");
  const API_URL = "http://localhost:8000";

  const [sysStats, setSysStats] = useState({
    cpu_usage: 12.5,
    ram_usage: 3.1,
    ram_total: 8.0,
    temperature: 46.8,
    status: "operational"
  });

  const [sessions, setSessions] = useState<any[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string>("");
  const [messages, setMessages] = useState<any[]>([]);
  const [newMessage, setNewMessage] = useState("");
  const [isSending, setIsSending] = useState(false);

  const [memories, setMemories] = useState<any[]>([]);
  const [newMemory, setNewMemory] = useState("");
  const [memorySearch, setMemorySearch] = useState("");

  const [plugins, setPlugins] = useState<any[]>([]);
  const [logs, setLogs] = useState<any[]>([]);

  const [voiceActive, setVoiceActive] = useState(false);
  const [spokenResponse, setSpokenResponse] = useState("");

  const [files, setFiles] = useState([
    { name: "jarvis_main.py", size: "12 KB", type: "Python Script" },
    { name: "memory_index.bin", size: "450 KB", type: "Index File" },
    { name: "system_config.json", size: "2.4 KB", type: "JSON Config" },
    { name: "weather_plugin.py", size: "5.1 KB", type: "Python Script" },
  ]);
  const [showSecurityPrompt, setShowSecurityPrompt] = useState(false);
  const [pendingFileAction, setPendingFileAction] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const [wsStatus, setWsStatus] = useState("disconnected");

  useEffect(() => {
    fetchSessions();
    fetchMemories();
    fetchPlugins();
    fetchLogs();
    fetchStats();

    const interval = setInterval(() => {
      fetchStats();
      fetchLogs();
    }, 4000);

    connectWebSocket();

    return () => {
      clearInterval(interval);
      if (wsRef.current) wsRef.current.close();
    };
  }, []);

  useEffect(() => {
    if (sessions.length > 0 && !currentSessionId) {
      loadSession(sessions[0].id);
    }
  }, [sessions]);

  const connectWebSocket = () => {
    try {
      const ws = new WebSocket("ws://localhost:8000/ws");
      wsRef.current = ws;

      ws.onopen = () => {
        setWsStatus("connected");
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
      };

      ws.onclose = () => {
        setWsStatus("disconnected");
        setTimeout(connectWebSocket, 5000);
      };
    } catch (e) {
      setWsStatus("disconnected");
    }
  };

  const fetchStats = async () => {
    try {
      const res = await fetch(`${API_URL}/api/system/stats`);
      if (res.ok) {
        const data = await res.json();
        setSysStats(data);
      }
    } catch (e) {}
  };

  const fetchSessions = async () => {
    try {
      const res = await fetch(`${API_URL}/api/sessions`);
      if (res.ok) {
        const data = await res.json();
        setSessions(data);
      }
    } catch (e) {}
  };

  const loadSession = async (id: string) => {
    try {
      const res = await fetch(`${API_URL}/api/sessions/${id}`);
      if (res.ok) {
        const data = await res.json();
        setCurrentSessionId(data.id);
        setMessages(data.messages || []);
      }
    } catch (e) {}
  };

  const createNewSession = async () => {
    try {
      const res = await fetch(`${API_URL}/api/sessions`, { method: "POST" });
      if (res.ok) {
        const data = await res.json();
        setSessions([data, ...sessions]);
        setCurrentSessionId(data.id);
        setMessages([]);
      }
    } catch (e) {}
  };

  const sendMessage = async () => {
    if (!newMessage.trim() || !currentSessionId) return;
    setIsSending(true);

    const userMsg = { sender: "user", content: newMessage, timestamp: new Date().toISOString() };
    setMessages(prev => [...prev, userMsg]);
    const promptText = newMessage;
    setNewMessage("");

    try {
      const res = await fetch(`${API_URL}/api/sessions/${currentSessionId}/messages`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: promptText })
      });

      if (res.ok) {
        const aiMsg = await res.json();
        setMessages(prev => [...prev, aiMsg]);

        setSpokenResponse(aiMsg.content.slice(0, 180) + "...");
        setVoiceActive(true);
        setTimeout(() => setVoiceActive(false), 5000);

        fetchMemories();
        fetchLogs();
      }
    } catch (e) {
      const fallbackAiMsg = {
        sender: "ai",
        content: `**[SYSTEM FAILSAFE TRIGGERED]** My cognitive processors are operating offline, but my core functions are fully intact. Based on your prompt "${promptText}", I recommend checking system services or network bounds.`,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, fallbackAiMsg]);
    } finally {
      setIsSending(false);
      fetchSessions();
    }
  };

  const fetchMemories = async () => {
    try {
      const url = memorySearch ? `${API_URL}/api/memories?query=${encodeURIComponent(memorySearch)}` : `${API_URL}/api/memories`;
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        setMemories(data);
      }
    } catch (e) {}
  };

  const handleAddMemory = async () => {
    if (!newMemory.trim()) return;
    try {
      const res = await fetch(`${API_URL}/api/memories`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: newMemory, category: "user_preference" })
      });
      if (res.ok) {
        setNewMemory("");
        fetchMemories();
        fetchLogs();
      }
    } catch (e) {}
  };

  const handleDeleteMemory = async (id: number) => {
    try {
      const res = await fetch(`${API_URL}/api/memories/${id}`, { method: "DELETE" });
      if (res.ok) {
        fetchMemories();
        fetchLogs();
      }
    } catch (e) {}
  };

  const fetchPlugins = async () => {
    try {
      const res = await fetch(`${API_URL}/api/plugins`);
      if (res.ok) {
        const data = await res.json();
        setPlugins(data);
      }
    } catch (e) {}
  };

  const togglePlugin = async (id: string, currentlyEnabled: boolean) => {
    try {
      const res = await fetch(`${API_URL}/api/plugins/${id}/toggle`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ enabled: !currentlyEnabled })
      });
      if (res.ok) {
        fetchPlugins();
        fetchLogs();
      }
    } catch (e) {}
  };

  const fetchLogs = async () => {
    try {
      const res = await fetch(`${API_URL}/api/logs`);
      if (res.ok) {
        const data = await res.json();
        setLogs(data);
      }
    } catch (e) {}
  };

  const triggerDeleteFile = (filename: string) => {
    setPendingFileAction(filename);
    setShowSecurityPrompt(true);
  };

  const confirmDeleteFile = () => {
    if (pendingFileAction) {
      setFiles(files.filter(f => f.name !== pendingFileAction));
      const logMsg = `Security Clearance Approved: Deleted file '${pendingFileAction}' safely.`;
      setLogs(prev => [{
        id: Date.now(),
        module: "Security",
        level: "WARNING",
        message: logMsg,
        timestamp: new Date().toISOString()
      }, ...prev]);
    }
    setShowSecurityPrompt(false);
    setPendingFileAction(null);
  };

  return (
    <div className="flex h-screen bg-cyber-darker text-slate-100 font-mono text-sm">

      {/* SIDEBAR MAIN NAV */}
      <div className="w-64 border-r border-cyber-border bg-cyber-dark flex flex-col justify-between">
        <div>
          {/* JARVIS HEADER */}
          <div className="p-6 border-b border-cyber-border flex items-center space-x-3 bg-slate-950/40">
            <div className="relative flex items-center justify-center">
              <div className="w-8 h-8 rounded-full border-2 border-cyber-blue animate-spin duration-[3000ms] border-dashed"></div>
              <div className="absolute w-4 h-4 rounded-full bg-cyber-blue animate-pulse"></div>
            </div>
            <div>
              <h1 className="font-bold text-cyber-blue tracking-widest cyber-glow-blue">JARVIS OS</h1>
              <p className="text-[10px] text-slate-500 uppercase tracking-widest flex items-center">
                <span className="w-1.5 h-1.5 bg-cyber-glow rounded-full mr-1.5 animate-pulse"></span>
                v1.0.0 Alpha
              </p>
            </div>
          </div>

          {/* MENUS */}
          <nav className="p-4 space-y-2">
            <button
              onClick={() => setActiveTab("chat")}
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-md transition-all ${activeTab === "chat" ? "bg-cyber-blue/10 text-cyber-blue border border-cyber-blue/30" : "text-slate-400 hover:text-white hover:bg-slate-900/40"}`}
            >
              <Terminal size={16} />
              <span>COGNITIVE HUB</span>
            </button>

            <button
              onClick={() => setActiveTab("memory")}
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-md transition-all ${activeTab === "memory" ? "bg-cyber-blue/10 text-cyber-blue border border-cyber-blue/30" : "text-slate-400 hover:text-white hover:bg-slate-900/40"}`}
            >
              <Database size={16} />
              <span>SEMANTIC MEMORY</span>
            </button>

            <button
              onClick={() => setActiveTab("plugins")}
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-md transition-all ${activeTab === "plugins" ? "bg-cyber-blue/10 text-cyber-blue border border-cyber-blue/30" : "text-slate-400 hover:text-white hover:bg-slate-900/40"}`}
            >
              <ToyBrick size={16} />
              <span>PLUGIN MARKET</span>
            </button>

            <button
              onClick={() => setActiveTab("files")}
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-md transition-all ${activeTab === "files" ? "bg-cyber-blue/10 text-cyber-blue border border-cyber-blue/30" : "text-slate-400 hover:text-white hover:bg-slate-900/40"}`}
            >
              <FolderOpen size={16} />
              <span>FILE NAVIGATOR</span>
            </button>

            <button
              onClick={() => setActiveTab("stats")}
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-md transition-all ${activeTab === "stats" ? "bg-cyber-blue/10 text-cyber-blue border border-cyber-blue/30" : "text-slate-400 hover:text-white hover:bg-slate-900/40"}`}
            >
              <Cpu size={16} />
              <span>DIAGNOSTICS</span>
            </button>
          </nav>
        </div>

        {/* SYSTEM STATUS FOOTER */}
        <div className="p-4 border-t border-cyber-border bg-slate-950/20 text-xs space-y-2">
          <div className="flex justify-between items-center text-slate-500">
            <span>SOCKET CHANNEL:</span>
            <span className={`font-semibold flex items-center ${wsStatus === "connected" ? "text-emerald-400" : "text-rose-400 animate-pulse"}`}>
              <Radio size={10} className="mr-1" />
              {wsStatus.toUpperCase()}
            </span>
          </div>
          <div className="flex justify-between items-center text-slate-500">
            <span>CPU TEMPERATURE:</span>
            <span className="text-orange-400 font-semibold">{sysStats.temperature}°C</span>
          </div>
        </div>
      </div>

      {/* CHAT SESSION LIST OR VIEW CONTAINER */}
      <div className="flex-1 flex flex-col bg-cyber-darker relative overflow-hidden">

        {/* TOP STATUS BAR */}
        <header className="h-16 border-b border-cyber-border flex items-center justify-between px-6 bg-cyber-dark/40 z-10">
          <div className="flex items-center space-x-3">
            <span className="text-slate-400 uppercase tracking-widest text-xs">MODULE:</span>
            <span className="text-cyber-blue font-bold uppercase tracking-widest text-xs cyber-glow-blue">{activeTab}</span>
          </div>

          <div className="flex items-center space-x-6">
            <div className="flex items-center space-x-2 text-xs text-slate-400">
              <Cpu size={14} className="text-cyber-blue" />
              <span>CPU: {sysStats.cpu_usage}%</span>
            </div>
            <div className="flex items-center space-x-2 text-xs text-slate-400">
              <Layers size={14} className="text-cyber-blue" />
              <span>RAM: {sysStats.ram_usage} / {sysStats.ram_total} GB</span>
            </div>
          </div>
        </header>

        {/* VOICE SYNTHESIS WAVEFORM AUDIO HUD */}
        {voiceActive && (
          <div className="absolute top-16 left-0 right-0 h-14 bg-cyber-blue/10 border-b border-cyber-blue/30 flex items-center justify-between px-6 animate-pulse z-20">
            <div className="flex items-center space-x-3">
              <Volume2 className="text-cyber-blue animate-bounce" size={18} />
              <div className="text-xs text-cyber-blue uppercase font-bold tracking-widest">vocalizing thought context:</div>
              <div className="text-xs text-slate-400 truncate max-w-xl italic">"{spokenResponse}"</div>
            </div>
            <div className="flex items-end space-x-1 h-6">
              {[...Array(8)].map((_, i) => (
                <div
                  key={i}
                  className="w-1 bg-cyber-blue animate-pulse"
                  style={{
                    height: `${Math.random() * 100}%`,
                    animationDelay: `${i * 0.15}s`,
                    animationDuration: '0.8s'
                  }}
                />
              ))}
            </div>
          </div>
        )}

        {/* CORE INTERFACE SWITCH */}
        <main className="flex-1 overflow-y-auto p-6 relative">

          {/* TAB 1: COGNITIVE HUB */}
          {activeTab === "chat" && (
            <div className="h-full flex space-x-6">
              <div className="w-64 flex flex-col border border-cyber-border rounded-lg bg-cyber-dark/30 p-4">
                <button
                  onClick={createNewSession}
                  className="w-full flex items-center justify-center space-x-2 p-2.5 rounded border border-dashed border-cyber-blue/40 text-cyber-blue hover:bg-cyber-blue/10 transition-all text-xs mb-4"
                >
                  <MessageSquarePlus size={14} />
                  <span>NEW THOUGHT THREAD</span>
                </button>

                <div className="flex-1 overflow-y-auto space-y-1 pr-1">
                  <div className="text-[10px] text-slate-500 uppercase font-bold tracking-wider mb-2">ACTIVE SESSIONS</div>
                  {sessions.map(s => (
                    <button
                      key={s.id}
                      onClick={() => loadSession(s.id)}
                      className={`w-full text-left px-3 py-2.5 rounded text-xs truncate transition-all ${currentSessionId === s.id ? "bg-cyber-blue/15 text-cyber-blue border-l-2 border-cyber-blue" : "text-slate-400 hover:text-white hover:bg-slate-900/30"}`}
                    >
                      {s.title}
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex-1 flex flex-col border border-cyber-border rounded-lg bg-cyber-dark/20 relative">
                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                  {messages.length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center text-center space-y-4 text-slate-500 max-w-md mx-auto">
                      <div className="w-12 h-12 rounded-full border border-cyber-blue/30 flex items-center justify-center text-cyber-blue animate-pulse">
                        <Terminal size={24} />
                      </div>
                      <h3 className="text-sm font-bold text-slate-300">SYSTEM COGNITIVE PROCESSOR ONLINE</h3>
                      <p className="text-xs text-slate-400">
                        Query me on complex planning, execute code logic in sandbox, orchestrate database indexes, or toggle custom plugins.
                      </p>
                    </div>
                  ) : (
                    messages.map((m, idx) => (
                      <div key={idx} className={`flex flex-col ${m.sender === "user" ? "items-end" : "items-start"}`}>
                        <div className="text-[10px] text-slate-500 uppercase tracking-widest mb-1">
                          {m.sender === "user" ? "COGNITIVE REQUESTOR" : "JARVIS OS RESPONSE"}
                        </div>
                        <div className={`p-4 rounded-lg max-w-3xl border text-xs leading-relaxed ${m.sender === "user" ? "bg-slate-900/60 border-cyber-border text-slate-200" : "bg-cyber-dark/60 border-cyber-blue/20 text-slate-100 shadow-[0_0_15px_rgba(0,240,255,0.03)]"}`}>
                          <div className="whitespace-pre-wrap">{m.content}</div>

                          {m.meta_data?.steps && (
                            <div className="mt-4 pt-3 border-t border-cyber-border space-y-2">
                              <div className="text-[10px] text-cyber-blue font-semibold uppercase tracking-widest flex items-center">
                                <Layers size={10} className="mr-1.5 animate-pulse" />
                                PLANNER STEP REASONING ANALYSIS
                              </div>
                              <div className="grid grid-cols-1 gap-2">
                                {m.meta_data.steps.map((st: any, sIdx: number) => (
                                  <div key={sIdx} className="bg-slate-950/80 p-2.5 rounded border border-cyber-border text-[11px] text-slate-400">
                                    <div className="flex justify-between items-center mb-1">
                                      <span className="font-bold text-slate-300">{st.step}</span>
                                      <span className="text-[9px] bg-cyber-blue/10 px-1.5 py-0.5 rounded text-cyber-blue uppercase tracking-widest font-semibold">{st.status}</span>
                                    </div>
                                    <div className="text-slate-500 text-[10px]">Action executed: <span className="text-slate-300 font-mono">{st.action}</span></div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    ))
                  )}
                </div>

                <div className="p-4 border-t border-cyber-border bg-slate-950/45">
                  <div className="flex space-x-2">
                    <input
                      type="text"
                      value={newMessage}
                      onChange={e => setNewMessage(e.target.value)}
                      onKeyDown={e => e.key === "Enter" && sendMessage()}
                      placeholder="Instruct system processor..."
                      className="flex-1 px-4 py-3 rounded cyber-input text-xs"
                      disabled={isSending}
                    />
                    <button
                      onClick={sendMessage}
                      className="px-5 rounded cyber-btn flex items-center justify-center space-x-2"
                      disabled={isSending}
                    >
                      <Send size={14} />
                      <span className="text-xs uppercase font-semibold">TRANSMIT</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: SEMANTIC MEMORY */}
          {activeTab === "memory" && (
            <div className="space-y-6">
              <div className="cyber-panel p-6 rounded-lg">
                <h3 className="text-cyber-blue font-bold text-sm tracking-widest uppercase mb-2 flex items-center">
                  <Database size={16} className="mr-2" />
                  COGNITIVE MEMORY MANAGEMENT
                </h3>
                <p className="text-xs text-slate-400 mb-6">
                  Manage the agent's highly modular vector memory structures. All inputs are embedded dynamically and evaluated using our bespoke, custom cosine-similarity indexing.
                </p>

                <div className="flex space-x-3 mb-6">
                  <input
                    type="text"
                    value={newMemory}
                    onChange={e => setNewMemory(e.target.value)}
                    placeholder="Input new long-term factual context..."
                    className="flex-1 px-4 py-3 rounded cyber-input text-xs"
                  />
                  <button
                    onClick={handleAddMemory}
                    className="px-6 rounded cyber-btn uppercase font-semibold text-xs flex items-center space-x-1"
                  >
                    <span>COMMIT TO MEMORY</span>
                  </button>
                </div>

                <div className="relative mb-6">
                  <Search className="absolute left-3 top-3 text-slate-500" size={16} />
                  <input
                    type="text"
                    value={memorySearch}
                    onChange={e => setMemorySearch(e.target.value)}
                    onKeyDown={e => e.key === "Enter" && fetchMemories()}
                    placeholder="Search memories via semantic cosine vector query..."
                    className="w-full pl-10 pr-4 py-3 rounded cyber-input text-xs"
                  />
                </div>

                <div className="space-y-3">
                  <div className="text-[10px] text-slate-500 uppercase tracking-widest font-semibold">ACTIVE COGNITIVE REGISTRY</div>
                  {memories.length === 0 ? (
                    <div className="p-4 border border-dashed border-cyber-border text-center text-slate-500 text-xs">
                      No memories located in storage registry. Write some text or execute queries to build memory nodes.
                    </div>
                  ) : (
                    memories.map((m, idx) => (
                      <div key={idx} className="p-4 border border-cyber-border rounded-lg bg-slate-950/40 flex justify-between items-center hover:border-cyber-blue/30 transition-all">
                        <div className="space-y-1.5">
                          <p className="text-xs text-slate-200">{m.content}</p>
                          <div className="flex items-center space-x-3 text-[10px] text-slate-500">
                            <span className="bg-slate-900 px-2 py-0.5 rounded text-cyber-blue uppercase font-bold text-[9px]">{m.category}</span>
                            <span>Recorded: {new Date(m.created_at).toLocaleTimeString()}</span>
                            {m.similarity !== undefined && (
                              <span className="text-emerald-400 font-bold">Similarity: {m.similarity.toFixed(4)}</span>
                            )}
                          </div>
                        </div>
                        <button
                          onClick={() => handleDeleteMemory(m.id)}
                          className="p-1.5 text-slate-500 hover:text-rose-400 rounded transition-colors"
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: PLUGINS */}
          {activeTab === "plugins" && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {plugins.map((pl, idx) => (
                  <div key={idx} className="cyber-panel p-6 rounded-lg flex flex-col justify-between space-y-4">
                    <div className="space-y-2">
                      <div className="flex justify-between items-start">
                        <h4 className="text-sm font-bold text-slate-200 uppercase tracking-widest">{pl.name}</h4>
                        <span className={`px-2 py-0.5 rounded text-[9px] uppercase tracking-widest font-bold ${pl.enabled ? "bg-emerald-400/10 text-emerald-400 border border-emerald-400/20" : "bg-slate-900 text-slate-500"}`}>
                          {pl.enabled ? "ENABLED" : "DISABLED"}
                        </span>
                      </div>
                      <p className="text-xs text-slate-400 leading-relaxed">{pl.description}</p>
                    </div>

                    <div className="pt-4 border-t border-cyber-border flex justify-between items-center text-xs text-slate-500">
                      <span>Config: <span className="font-mono text-slate-300">{JSON.stringify(pl.config)}</span></span>
                      <button
                        onClick={() => togglePlugin(pl.id, pl.enabled)}
                        className={`px-4 py-2 rounded text-xs uppercase font-bold transition-all ${pl.enabled ? "bg-rose-950/30 text-rose-400 border border-rose-900/40 hover:bg-rose-900/30" : "bg-emerald-950/30 text-emerald-400 border border-emerald-900/40 hover:bg-emerald-900/30"}`}
                      >
                        {pl.enabled ? "DEACTIVATE" : "ACTIVATE"}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 4: FILES */}
          {activeTab === "files" && (
            <div className="space-y-6">
              <div className="cyber-panel p-6 rounded-lg">
                <h3 className="text-cyber-blue font-bold text-sm tracking-widest uppercase mb-2 flex items-center">
                  <FolderOpen size={16} className="mr-2" />
                  JARVIS SECURE FILE NAVIGATOR
                </h3>
                <p className="text-xs text-slate-400 mb-6">
                  Access local OS file stores. Dangerous file modifications require strict security approval checkpoints before execution.
                </p>

                <div className="border border-cyber-border rounded-lg overflow-hidden">
                  <div className="grid grid-cols-4 gap-4 p-3 bg-slate-950/60 border-b border-cyber-border text-[10px] text-slate-500 font-bold uppercase tracking-widest">
                    <div className="col-span-2">FILENAME</div>
                    <div>FILE SIZE</div>
                    <div className="text-right">ACTIONS</div>
                  </div>

                  <div className="divide-y divide-cyber-border">
                    {files.map((f, idx) => (
                      <div key={idx} className="grid grid-cols-4 gap-4 p-4 items-center text-xs hover:bg-slate-900/20">
                        <div className="col-span-2 flex items-center space-x-3">
                          <FileCode size={16} className="text-cyber-blue" />
                          <span className="text-slate-200 font-semibold">{f.name}</span>
                        </div>
                        <div className="text-slate-400">{f.size}</div>
                        <div className="text-right">
                          <button
                            onClick={() => triggerDeleteFile(f.name)}
                            className="px-3 py-1.5 rounded bg-rose-950/20 text-rose-400 hover:bg-rose-900/30 text-[10px] uppercase font-bold tracking-widest border border-rose-900/30 transition-all"
                          >
                            DELETE
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 5: DIAGNOSTICS & RAW CONSOLE */}
          {activeTab === "stats" && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="cyber-panel p-6 rounded-lg space-y-4">
                  <h4 className="text-xs text-cyber-blue font-bold uppercase tracking-widest">DIAGNOSTIC PROCESS CORES</h4>
                  <div className="space-y-3 text-xs">
                    <div>
                      <div className="flex justify-between text-slate-400 mb-1">
                        <span>CPU THREAD UTILIZATION</span>
                        <span className="text-cyber-blue font-semibold">{sysStats.cpu_usage}%</span>
                      </div>
                      <div className="w-full bg-slate-950 h-2 rounded border border-cyber-border overflow-hidden">
                        <div className="bg-cyber-blue h-full" style={{ width: `${sysStats.cpu_usage}%` }} />
                      </div>
                    </div>

                    <div>
                      <div className="flex justify-between text-slate-400 mb-1">
                        <span>MEMORY ALLOCATION</span>
                        <span className="text-cyber-blue font-semibold">{sysStats.ram_usage} GB / {sysStats.ram_total} GB</span>
                      </div>
                      <div className="w-full bg-slate-950 h-2 rounded border border-cyber-border overflow-hidden">
                        <div className="bg-cyber-blue h-full" style={{ width: `${(sysStats.ram_usage / sysStats.ram_total) * 100}%` }} />
                      </div>
                    </div>
                  </div>
                </div>

                <div className="cyber-panel p-6 rounded-lg space-y-4">
                  <h4 className="text-xs text-cyber-blue font-bold uppercase tracking-widest">FREQUENCY SIGNAL HUBS</h4>
                  <div className="flex items-end space-x-1.5 h-24 pt-4 justify-between">
                    {[...Array(24)].map((_, i) => {
                      const heights = [40, 55, 65, 80, 45, 30, 95, 80, 70, 60, 50, 40, 70, 85, 90, 100, 60, 40, 55, 75, 90, 80, 50, 30];
                      return (
                        <div
                          key={i}
                          className="w-2.5 bg-gradient-to-t from-cyber-blue to-cyan-400 rounded-t-sm"
                          style={{ height: `${heights[i]}%` }}
                        />
                      );
                    })}
                  </div>
                </div>
              </div>

              <div className="cyber-panel p-6 rounded-lg">
                <div className="flex justify-between items-center mb-4">
                  <h4 className="text-xs text-cyber-blue font-bold uppercase tracking-widest flex items-center">
                    <Terminal size={14} className="mr-2" />
                    REAL-TIME SYSTEM RAW CONSOLE
                  </h4>
                  <div className="flex items-center space-x-2 text-[10px] text-slate-500">
                    <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                    <span>LOGSTREAM ACTIVE</span>
                  </div>
                </div>

                <div className="bg-slate-950 p-4 rounded border border-cyber-border h-64 overflow-y-auto font-mono text-xs space-y-1.5">
                  {logs.length === 0 ? (
                    <div className="text-slate-600 text-center py-10">No logs captured yet in database registry. Try transmitting text.</div>
                  ) : (
                    logs.map((log, idx) => (
                      <div key={idx} className={`flex space-x-2 ${log.level === 'ERROR' ? 'text-rose-400' : log.level === 'WARNING' ? 'text-amber-400' : 'text-slate-400'}`}>
                        <span className="text-slate-600">[{new Date(log.timestamp).toLocaleTimeString()}]</span>
                        <span className="font-semibold text-slate-500">[{log.module}]</span>
                        <span className="font-bold">[{log.level}]</span>
                        <span>{log.message}</span>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>
          )}

        </main>
      </div>

      {/* SECURITY VERIFICATION MODAL */}
      {showSecurityPrompt && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-md flex items-center justify-center z-50">
          <div className="w-full max-w-md cyber-panel p-6 rounded-lg border-2 border-rose-500/40 bg-cyber-dark text-slate-100 shadow-[0_0_30px_rgba(239,68,68,0.2)]">
            <div className="flex items-center space-x-3 mb-4 text-rose-400">
              <ShieldAlert size={28} className="animate-pulse" />
              <div>
                <h4 className="font-bold text-sm uppercase tracking-widest">SECURITY VERIFICATION REQUIRED</h4>
                <p className="text-[10px] text-rose-400/80 uppercase font-bold tracking-wider">Level 4 Clearance Check</p>
              </div>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed mb-6">
              Attention. The system has intercepted a potentially dangerous instruction command: <span className="font-bold text-rose-400">delete file '{pendingFileAction}'</span>. Please confirm this action is authorized.
            </p>

            <div className="flex space-x-3 justify-end">
              <button
                onClick={() => { setShowSecurityPrompt(false); setPendingFileAction(null); }}
                className="px-4 py-2 rounded text-xs uppercase font-bold tracking-widest bg-slate-900 border border-cyber-border hover:border-slate-500 transition-all text-slate-400"
              >
                ABORT
              </button>
              <button
                onClick={confirmDeleteFile}
                className="px-5 py-2 rounded text-xs uppercase font-bold tracking-widest bg-rose-950 text-rose-400 border border-rose-600/40 hover:bg-rose-600 hover:text-white transition-all"
              >
                CONFIRM DELETION
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
