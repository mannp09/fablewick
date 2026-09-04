import { Route, Routes } from 'react-router-dom';
import Header from './components/Header';
import Library from './pages/Library';
import Reader from './pages/Reader';
import Heritage from './pages/Heritage';
import HeritageReader from './pages/HeritageReader';

export default function App() {
  return (
    <>
      <Header />
      <Routes>
        <Route path="/" element={<Library />} />
        <Route path="/read/:slug" element={<Reader />} />
        <Route path="/heritage" element={<Heritage />} />
        <Route path="/heritage/read/:slug" element={<HeritageReader />} />
      </Routes>
    </>
  );
}
