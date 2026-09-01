export default function Topbar({ onMenu, title }) {
  return <header className="topbar"><button className="menu-button" onClick={onMenu} aria-label="Open navigation">☰</button><div><span className="eyebrow">Merchant workspace</span><h1>{title}</h1></div><div className="mode-pill"><span /> Simulation / Test Mode</div></header>
}
