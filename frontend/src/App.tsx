import { BrowserRouter, Route, Routes } from 'react-router';
import Home from './pages/home';
import Project from './pages/project';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient();

export default function App() {
    return (
        <QueryClientProvider client={queryClient}>
            <BrowserRouter>
                <Routes>
                    <Route path="/" element={<Home />} />
                    <Route path="/project/:projectId" element={<Project />} />
                </Routes>
            </BrowserRouter>
        </QueryClientProvider>
    );
}
