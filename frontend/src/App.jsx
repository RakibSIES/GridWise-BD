import React, { useEffect, useState } from 'react';

function App() {
  const [data, setData] = useState(null);
  const [selectedDivisionIndex, setSelectedDivisionIndex] = useState(0);
  const [activeDivision, setActiveDivision] = useState(null);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isAcademicView, setIsAcademicView] = useState(false);
  const [isSearchModalOpen, setIsSearchModalOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [cardOffset, setCardOffset] = useState(0);

  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/metrics')
      .then(res => res.json())
      .then(resData => {
        setData(resData);
        if (resData.divisions && resData.divisions.length > 0) {
          setActiveDivision(resData.divisions[0]);
        }
      })
      .catch(err => console.error("Error fetching metrics:", err));
  }, []);

  const divisionsList = data?.divisions || [
    { id: 0, name: 'Dhaka Division (Capital)', substation: '400kV Meghnaghat', deficit: '450 MW', outage: '3 - 4 Hours', driver: 'Extreme Ambient Heat & Industrial Peak', risk: 'High Risk', riskColor: 'rose', arima_auc: 0.72, hybrid_auc: 0.88 },
    { id: 1, name: 'Mymensingh Division', substation: 'Rural Transmission Grid', deficit: '180 MW', outage: '4 - 5 Hours', driver: 'Rural Distribution Feeder Overload', risk: 'High Risk', riskColor: 'rose', arima_auc: 0.70, hybrid_auc: 0.90 },
    { id: 2, name: 'Rangpur Division', substation: 'Northern Interconnect', deficit: '95 MW', outage: '1 - 2 Hours', driver: 'Cross-Regional Transmission Lag', risk: 'Moderate Risk', riskColor: 'amber', arima_auc: 0.74, hybrid_auc: 0.91 },
    { id: 3, name: 'Chattogram Division (Industrial & Port)', substation: '230kV Anwara Grid', deficit: '210 MW', outage: '2 - 3 Hours', driver: 'Gas Supply Shortage', risk: 'High Risk', riskColor: 'rose', arima_auc: 0.71, hybrid_auc: 0.86 },
    { id: 4, name: 'Khulna Division (Southern Coast)', substation: 'Rampal Transmission Line', deficit: '140 MW', outage: '2 Hours', driver: 'Plant Maintenance', risk: 'Moderate Risk', riskColor: 'amber', arima_auc: 0.73, hybrid_auc: 0.85 },
    { id: 5, name: 'Rajshahi Division (North-West Agri Hub)', substation: 'Bheramara Interconnect', deficit: '160 MW', outage: '3 - 4 Hours', driver: 'Irrigation Surge', risk: 'Moderate Risk', riskColor: 'amber', arima_auc: 0.75, hybrid_auc: 0.87 },
    { id: 6, name: 'Sylhet Division (Eastern Surma Valley)', substation: 'Bibiyana Gas Plant Subgrid', deficit: '25 MW', outage: '<30 Mins', driver: 'Low Risk', risk: 'Low Risk', riskColor: 'emerald', arima_auc: 0.76, hybrid_auc: 0.88 },
    { id: 7, name: 'Barishal Division (Delta Coastal)', substation: 'Payra Thermal Subgrid', deficit: '35 MW', outage: '<45 Mins', driver: 'Low Risk', risk: 'Low Risk', riskColor: 'emerald', arima_auc: 0.78, hybrid_auc: 0.89 },
    { id: 8, name: 'Cumilla Division (Eastern Hub)', substation: 'Tripura Interconnect', deficit: '115 MW', outage: '1.5 - 2.5 Hours', driver: 'Transformer Heat', risk: 'Moderate Risk', riskColor: 'amber', arima_auc: 0.72, hybrid_auc: 0.86 }
  ];

  const filteredDivisions = divisionsList.filter(div =>
    div.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    div.substation.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleNextSlide = () => {
    if (cardOffset + 3 < divisionsList.length) {
      setCardOffset(cardOffset + 3);
    }
  };

  const handlePrevSlide = () => {
    if (cardOffset - 3 >= 0) {
      setCardOffset(cardOffset - 3);
    }
  };

  const handleSelectSearchedDiv = (div) => {
    setActiveDivision(div);
    setIsSearchModalOpen(false);
    setSearchQuery('');
    const elem = document.getElementById('division-alerts');
    if (elem) elem.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="bg-gray-100 text-gray-800 antialiased flex flex-col items-center min-h-screen">
      <div className="w-full max-w-[1240px] bg-white shadow-2xl relative overflow-hidden min-h-screen">

        {/* Top Header */}
        <section className="bg-[#5bb334] text-white text-xs px-6 lg:px-12 py-2 flex flex-wrap justify-between items-center font-medium">
          <div className="flex items-center space-x-6">
            <span>(880) 2-9556100</span>
            <span>telemetry@gridwise-bd.gov</span>
          </div>
          <div className="flex items-center space-x-6">
            <span>English | বাংলা</span>
            <span className="inline-flex items-center gap-1.5 bg-black/15 px-2.5 py-0.5 rounded-full text-[11px] font-semibold">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-200 animate-pulse"></span>
              System Online
            </span>
          </div>
        </section>

        {/* Navbar */}
        <header className="bg-[#f7faf4] px-6 lg:px-12 py-5 flex items-center justify-between border-b border-gray-100">
          <a className="flex items-center space-x-2 text-2xl font-black text-gray-900 tracking-tight" href="#">
            <span>GridWise</span>
            <span className="text-[#5bb334] flex items-center">-BD</span>
          </a>
          <nav className="flex items-center space-x-6">
            <button
              onClick={() => setIsSearchModalOpen(true)}
              className="flex items-center gap-2 bg-[#53ad37] hover:bg-[#46952e] text-white px-5 py-2.5 rounded-full font-medium text-sm transition-all shadow-sm"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-4.35-4.35M16.65 11a5.65 5.65 0 11-11.3 0 5.65 5.65 0 0111.3 0z"></path>
              </svg>
              Search My Area
            </button>

            {/* Hamburger Button */}
            <div className="relative">
              <button
                onClick={() => setIsMenuOpen(!isMenuOpen)}
                className="p-1 text-gray-700 hover:text-black focus:outline-none"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <line strokeLinecap="round" strokeWidth="2.5" x1="4" x2="20" y1="6" y2="6"></line>
                  <line strokeLinecap="round" strokeWidth="2.5" x1="4" x2="20" y1="12" y2="12"></line>
                  <line strokeLinecap="round" strokeWidth="2.5" x1="4" x2="20" y1="18" y2="18"></line>
                </svg>
              </button>
              {isMenuOpen && (
                <div className="absolute right-0 mt-3 w-64 bg-white rounded-xl shadow-xl border border-gray-100 py-2 z-50">
                  <a href="#defense" onClick={() => setIsMenuOpen(false)} className="block px-4 py-2.5 text-xs font-semibold text-gray-700 hover:bg-gray-100 hover:text-[#5bb334]">Academic & Research Defense</a>
                  <a href="#pgcb-docs" onClick={() => setIsMenuOpen(false)} className="block px-4 py-2.5 text-xs font-semibold text-gray-700 hover:bg-gray-100 hover:text-[#5bb334]">PGCB Model Documentation</a>
                  <a href="#api-status" onClick={() => setIsMenuOpen(false)} className="block px-4 py-2.5 text-xs font-semibold text-gray-700 hover:bg-gray-100 hover:text-[#5bb334]">API Telemetry Status</a>
                </div>
              )}
            </div>
          </nav>
        </header>

        {/* Hero Section */}
        <section className="grid grid-cols-1 lg:grid-cols-12 min-h-[460px] relative bg-[#f7faf4]">
          <div className="lg:col-span-6 px-8 lg:px-14 pt-10 pb-20 flex flex-col justify-between">
            <div className="max-w-xl">
              <h1 className="text-4xl lg:text-[46px] font-extrabold text-gray-900 leading-[1.15]">
                Predict 24-Hour Load-Shedding Across <span className="text-[#5bb334]">Bangladesh</span>
              </h1>
              <p className="mt-4 text-gray-600 text-sm md:text-base">
                Day-ahead regional power deficit alerts, expected outage durations, and grid forecasts for citizens, hospitals, and local businesses.
              </p>
            </div>
            <div className="grid grid-cols-3 gap-6 pt-12">
              <div>
                <div className="text-3xl font-extrabold text-gray-900">9</div>
                <div className="text-xs text-gray-500 font-medium mt-1">Divisions Monitored</div>
              </div>
              <div>
                <div className="text-3xl font-extrabold text-gray-900">24h</div>
                <div className="text-xs text-gray-500 font-medium mt-1">Forecast Horizon</div>
              </div>
              <div>
                <div className="text-3xl font-extrabold text-gray-900">98.2%</div>
                <div className="text-xs text-gray-500 font-medium mt-1">Reliability Rate</div>
              </div>
            </div>
          </div>
          <div className="lg:col-span-6 relative min-h-[300px] lg:min-h-full overflow-hidden">
            <img
              alt="Power grid Bangladesh"
              className="w-full h-full object-cover"
              src="https://lh3.googleusercontent.com/aida-public/AB6AXuCq6yDXfup0KyueSN8yuy-vSV1tqxvdzLjxtL4XtI1Or6hZEyc4_Zm6iJamgCOYCB4UkDW7dOcIgg2cgfsy7_L8KMQoBCOi9VksxOYl0YEr60MBSIGiFHu0OEUz9ZCzFj6lXkokFjBHYiolcPQl0ru4zrWrY-53BARH5sEpv4IhjOgV2ldgVEmFGj5_Zc3kaEuhJwXhZV-zXRVqX_R-NV1xe7BwwOGma_-F3dx9PQ"
            />
          </div>
        </section>

        {/* Quick Filter Bar */}
        <div className="relative px-6 lg:px-12 -mt-10 z-20">
          <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-4 lg:p-5 flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex-1 px-4 md:border-r border-gray-200">
              <label className="block text-xs font-bold text-gray-900">Select Division</label>
              <select
                value={selectedDivisionIndex}
                onChange={(e) => {
                  const idx = Number(e.target.value);
                  setSelectedDivisionIndex(idx);
                  setActiveDivision(divisionsList[idx]);
                }}
                className="w-full text-xs text-gray-800 font-semibold mt-1 p-0 border-none bg-transparent"
              >
                {divisionsList.map((div, idx) => (
                  <option key={div.name} value={idx}>{div.name}</option>
                ))}
              </select>
            </div>
            <button
              onClick={() => {
                const elem = document.getElementById('division-alerts');
                if (elem) elem.scrollIntoView({ behavior: 'smooth' });
              }}
              className="bg-[#5bb334] hover:bg-[#4da02a] text-white px-7 py-3 rounded-full text-sm font-semibold shrink-0"
            >
              Check 24-Hour Risk
            </button>
          </div>
        </div>

        {/* Dark Cards Slider Section */}
        <section className="mt-8 mx-3 md:mx-6 bg-[#212427] rounded-3xl p-6 lg:p-10 text-white relative" id="division-alerts">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
            <div>
              <h2 className="text-2xl md:text-3xl font-extrabold tracking-tight">24-Hour Regional Load-Shedding Forecast</h2>
              <p className="text-xs text-gray-400 mt-1">Official Day-Ahead dispatch deficit projection across all 9 administrative divisions</p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 bg-gray-800/80 px-3 py-1.5 rounded-full border border-gray-700">
                <span className="text-xs text-gray-300 font-medium">Academic & Technical View</span>
                <button
                  onClick={() => setIsAcademicView(!isAcademicView)}
                  className={`w-8 h-4.5 rounded-full p-0.5 transition ${isAcademicView ? 'bg-[#5bb334]' : 'bg-gray-600'}`}
                >
                  <div className={`w-3.5 h-3.5 bg-white rounded-full transform transition ${isAcademicView ? 'translate-x-3.5' : 'translate-x-0'}`}></div>
                </button>
              </div>
            </div>
          </div>

          {/* Dynamic Active Division Focus Banner */}
          {activeDivision && (
            <div className="mb-6 bg-gray-800/60 border border-[#5bb334]/40 rounded-2xl p-4 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
              <div>
                <span className="text-xs text-[#5bb334] font-bold uppercase">Focus Area Selected</span>
                <h3 className="text-xl font-bold text-white mt-0.5">{activeDivision.name}</h3>
                <p className="text-xs text-gray-300">Driver: {activeDivision.driver}</p>
              </div>
              <div className="flex items-center gap-3">
                <div className="bg-black/40 px-3 py-1.5 rounded-xl border border-gray-700 text-xs">
                  <span className="text-gray-400 block text-[10px]">Deficit Volume</span>
                  <span className="font-extrabold text-rose-400">{activeDivision.deficit}</span>
                </div>
                <div className="bg-black/40 px-3 py-1.5 rounded-xl border border-gray-700 text-xs">
                  <span className="text-gray-400 block text-[10px]">Outage Duration</span>
                  <span className="font-bold text-white">{activeDivision.outage}</span>
                </div>
              </div>
            </div>
          )}

          {/* 3 Active Slider Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {divisionsList.slice(cardOffset, cardOffset + 3).map((div) => (
              <div key={div.id} className="group relative rounded-2xl overflow-hidden bg-gray-900/80 border border-gray-800 shadow-xl flex flex-col justify-end min-h-[380px]">
                <div className="absolute top-4 left-4 z-10">
                  <span className={`bg-${div.riskColor}-500/90 text-white text-[11px] font-bold px-2.5 py-1 rounded-full uppercase`}>
                    {div.risk}
                  </span>
                </div>
                <div className="relative p-5 z-10">
                  <h3 className="text-xl font-bold text-white tracking-tight">{div.name}</h3>
                  <p className="text-xs text-gray-300 mt-1">Substation: {div.substation}</p>
                  <div className="mt-3 pt-3 border-t border-gray-700/70 space-y-1.5 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="text-gray-300">Estimated Deficit:</span>
                      <span className="font-extrabold text-rose-400 text-sm">{div.deficit}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-300">Expected Outage:</span>
                      <span className="font-bold text-white bg-black/40 px-2 py-0.5 rounded border border-gray-700">{div.outage}</span>
                    </div>
                    <div className="pt-1 text-[11px] text-gray-300">
                      <span className="text-gray-400">Primary Driver:</span> {div.driver}
                    </div>
                    {isAcademicView && (
                      <div className="pt-2 border-t border-gray-800 text-[11px] flex justify-between text-[#5bb334] font-mono">
                        <span>ARIMA: {div.arima_auc}</span>
                        <span>Stage-2 Hybrid: {div.hybrid_auc}</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Slider Pagination Controls */}
          <div className="mt-6 pt-5 border-t border-gray-800 flex items-center justify-between">
            <span className="text-xs text-gray-400">Showing {cardOffset + 1} - {Math.min(cardOffset + 3, divisionsList.length)} of {divisionsList.length} Divisions</span>
            <div className="flex items-center space-x-3">
              <button
                onClick={handlePrevSlide}
                disabled={cardOffset === 0}
                className={`w-10 h-10 rounded-full border border-gray-700 bg-gray-800 text-white flex items-center justify-center transition ${cardOffset === 0 ? 'opacity-40 cursor-not-allowed' : 'hover:border-gray-500'}`}
              >
                &lt;
              </button>
              <button
                onClick={handleNextSlide}
                disabled={cardOffset + 3 >= divisionsList.length}
                className={`w-10 h-10 rounded-full bg-white text-gray-900 flex items-center justify-center shadow-md transition ${cardOffset + 3 >= divisionsList.length ? 'opacity-40 cursor-not-allowed' : 'hover:bg-gray-200'}`}
              >
                &gt;
              </button>
            </div>
          </div>
        </section>

        {/* SEARCH MY AREA MODAL */}
        {isSearchModalOpen && (
          <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="bg-white rounded-2xl p-6 w-full max-w-lg shadow-2xl relative">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-bold text-gray-900">Search Your Local Area / Division</h3>
                <button
                  onClick={() => setIsSearchModalOpen(false)}
                  className="text-gray-400 hover:text-black font-bold text-lg"
                >
                  ✕
                </button>
              </div>
              <input
                type="text"
                placeholder="Type division or substation (e.g. Dhaka, Meghnaghat)..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full p-3 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-[#5bb334] focus:outline-none mb-4"
              />
              <div className="max-h-60 overflow-y-auto space-y-2">
                {filteredDivisions.length > 0 ? (
                  filteredDivisions.map((div) => (
                    <div
                      key={div.name}
                      onClick={() => handleSelectSearchedDiv(div)}
                      className="p-3 rounded-xl border border-gray-100 hover:bg-[#f2f9ed] cursor-pointer flex justify-between items-center transition"
                    >
                      <div>
                        <h4 className="font-bold text-sm text-gray-900">{div.name}</h4>
                        <p className="text-xs text-gray-500">Substation: {div.substation}</p>
                      </div>
                      <span className="text-xs font-bold text-rose-500 bg-rose-50 px-2 py-1 rounded">{div.deficit} Deficit</span>
                    </div>
                  ))
                ) : (
                  <p className="text-xs text-gray-400 text-center py-4">No matching division found.</p>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Footer */}
        <footer className="border-t border-gray-200 py-6 px-6 lg:px-12 text-xs text-gray-500 flex justify-between items-center">
          <p>© 2026 PGCB & GridWise-BD Citizen Intelligence Portal.</p>
        </footer>
      </div>
    </div>
  );
}

export default App;