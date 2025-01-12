import { ColorPicker } from '@/components/color-picker';
import { Grid } from '@/components/grid';
import { Button } from '@/components/ui/button';
import {
    applyChanges,
    DEFAULT_DRAW_STATE,
    fetchProjectState,
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

    const version = searchParams.get('version');

    const query = useQuery({
        queryKey: ['project', { projectId }, 'version', version],
        queryFn: async () => {
            if (!projectId) throw new Error('No project id found!');
            return await fetchProjectState(projectId, version);
        },
    });

    return (
        <div className="container flex flex-col mx-auto p-4">
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
                    colors={applyChanges(
                        (query.data?.state ?? DEFAULT_DRAW_STATE).chunks,
                        actions,
                    )}
                    cols={query.data?.state.cols ?? 16}
                    editMode={isEditing}
                    onPixelClick={(index) => {
                        if (!isEditing) return;
                        setActions((actions) => [
                            ...actions,
                            {
                                index: index,
                                color: currentColor,
                            },
                        ]);
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
