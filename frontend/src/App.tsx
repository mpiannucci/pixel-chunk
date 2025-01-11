import { BrowserRouter, Route, Routes } from 'react-router';
import Home from './pages/home';
import Project from './pages/project';

export default function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/project/:projectId" element={<Project />} />
            </Routes>
        </BrowserRouter>
    );
}
