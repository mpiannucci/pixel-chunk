import { LoadingSpinner } from '@/components/loading-spinner';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { createNewProject } from '@/state';
import { Settings } from 'lucide-react';
import { useState } from 'react';
import { useNavigate } from 'react-router';

export default function Home() {
    const navigate = useNavigate();
    const [isCreating, setIsCreating] = useState(false);
    const [showOptions, setShowOptions] = useState(false);
    const [projectWidth, setProjectWidth] = useState(8);
    const [projectHeight, setProjectHeight] = useState(8);

    return (
        <div className="flex flex-col items-center justify-center h-screen">
            <h1 className="text-2xl font-bold mb-4">Start creating</h1>
            <div className="flex flex-row items-center justify-center space-x-2">
                <Button
                    disabled={isCreating}
                    onClick={async () => {
                        // Show loading spinner,
                        setIsCreating(true);

                        try {
                            // Create new project
                            const newProjectId = await createNewProject(
                                projectWidth,
                                projectHeight,
                            );
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
                <Button
                    className="w-8"
                    variant={'ghost'}
                    onClick={() => setShowOptions((prev) => !prev)}
                >
                    <Settings />
                </Button>
            </div>
            <div
                className="mt-4 flex flex-col items-center space-y-4"
                style={{ visibility: showOptions ? 'visible' : 'hidden' }}
            >
                <div className="flex flex-row justify-between items-center space-x-2 w-42">
                    <label htmlFor="width">Width (px)</label>
                    <Input
                        id="width"
                        type="number"
                        value={projectWidth}
                        min={1}
                        max={256}
                        className="w-16"
                        onChange={(e) =>
                            setProjectWidth(parseInt(e.target.value))
                        }
                    />
                </div>
                <div className="flex flex-row justify-between items-center space-x-2 w-42">
                    <label htmlFor="height">Height (px)</label>
                    <Input
                        id="height"
                        type="number"
                        value={projectHeight}
                        min={1}
                        max={256}
                        className="w-16"
                        onChange={(e) =>
                            setProjectHeight(parseInt(e.target.value))
                        }
                    />
                </div>
            </div>
        </div>
    );
}
