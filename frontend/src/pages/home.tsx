import { Button } from "@/components/ui/button";


export default function Home() {
    return (
        <div className="flex flex-col items-center justify-center h-screen">
            <h1 className="text-2xl font-bold">
                Start creating
            </h1>
            <Button className="m-8" onClick={async () => {
                // TODO: Show loading spinner,
                // TODO: Create new project
                // TODO: Redirect to project page
            }}>New Project</Button>
        </div>
    );
}