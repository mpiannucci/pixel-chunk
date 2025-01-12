import { LoadingSpinner } from '@/components/loading-spinner';
import { Button } from '@/components/ui/button';
import { createNewProject } from '@/state';
import { useState } from 'react';
import { useNavigate } from 'react-router';

export default function Home() {
    const navigate = useNavigate();
    const [isCreating, setIsCreating] = useState(false);

    return (
        <div className="flex flex-col items-center justify-center h-screen">
            <h1 className="text-2xl font-bold">Start creating</h1>
            <Button
                className="m-8"
                disabled={isCreating}
                onClick={async () => {
                    // Show loading spinner,
                    setIsCreating(true);

                    try {
                        // Create new project
                        const newProjectId = await createNewProject();
                        // Navigate to the new project page
                        setIsCreating(false);
                        navigate(`/project/${newProjectId}`);
                    } catch (e) {
                        console.error(e);

                        // TODO: Actually do something about the error
                        setIsCreating(false);
                    }
                }}
            >
                {isCreating && (
                    <div className="flex flex-row items-center space-x-2">
                        <a>Creating project</a>
                        <LoadingSpinner
                            size={16}
                            color="white"
                            borderWidth={2}
                        />
                    </div>
                )}
                {!isCreating && <a>New Project</a>}
            </Button>
        </div>
    );
}
