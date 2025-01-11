import { ColorPicker } from '@/components/color-picker';
import { Grid } from '@/components/grid';
import { Button } from '@/components/ui/button';
import {
    DEFAULT_DRAW_STATE,
    parseProjectState,
    ProjectState,
    UpdateAction,
} from '@/state';
import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { Link, useParams, useSearchParams } from 'react-router';

export default function Project() {
    const { projectId } = useParams();
    const [searchParams, setSearchParams] = useSearchParams();
    const [isEditing, setIsEditing] = useState(false);
    const [currentColor, setCurrentColor] = useState('#ffffffff');
    const [actions, setActions] = useState<UpdateAction[]>([]);
    const [rebaseStrategy, setRebaseStrategy] = useState<'ours' | 'theirs'>(
        'ours',
    );

    const query = useQuery({
        queryKey: ['project', { projectId }],
        queryFn: async () => {
            const response = await fetch(`/projects/${projectId}`);
            const json = await response.json();
            return parseProjectState(json);
        },
    });

    console.log(query.data);

    return (
        <div className="container flex flex-col mx-auto">
            <div className="flex flex-row items-center justify-between">
                <h2 className="text-xl font-bold mt-8 mb-4">
                    Project {projectId}
                </h2>
                {!searchParams.get('version') && !isEditing && (
                    <Button onClick={() => setIsEditing(true)}>Edit</Button>
                )}
            </div>
            <div className="flex flex-row justify-between flex-wrap">
                <Grid
                    state={query.data?.state ?? DEFAULT_DRAW_STATE}
                    editMode={isEditing}
                    onPixelClick={(index) => {
                        if (!isEditing) return;
                        console.log('TODO: Implement onPixelClick');
                    }}
                />
                {isEditing && (
                    <div className="flex flex-col space-y-4">
                        <h3 className="text-lg font-medium">Edit</h3>
                        <ColorPicker
                            selectedColor={currentColor}
                            onColorChange={setCurrentColor}
                        />
                        <Button onClick={() => setIsEditing(false)}>
                            Save
                        </Button>
                    </div>
                )}
                {!isEditing && (
                    <div className="flex flex-col">
                        <h3 className="text-lg font-medium">Versions</h3>
                        <ul className="list-disc pl-4">
                            {query.data?.versions.map((version) => (
                                <li
                                    key={version.id}
                                    className="text-sm hover:text-blue-400 underline"
                                >
                                    <Link
                                        to={`/project/${projectId}?version=${version.id}`}
                                    >
                                        {version.message} -{' '}
                                        {version.date.toLocaleString()}
                                    </Link>
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>
        </div>
    );
}
