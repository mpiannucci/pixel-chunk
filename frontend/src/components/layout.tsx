import { Outlet } from 'react-router-dom';

export default function Layout() {
    return (
        <>
            <div className="flex flex-col h-screen">
                <div className="flex-1">
                    <Outlet />
                </div>
            </div>
            <footer className='w-full items-center space-x-4 mx-auto px-4 flex flex-row justify-center'>
                <a className='underline hover:text-blue-400' href="https://github.com/mpiannucci/pixel-chunk" target="_blank">Checkout the source on Github</a>
                <a className='underline hover:text-blue-400' href="https://icechunk.io" target="_blank">About icechunk</a>
            </footer>
        </>
    );
}
