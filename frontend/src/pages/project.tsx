import { ColorPicker } from '@/components/color-picker';
import { Grid } from '@/components/grid';
import { LoadingSpinner } from '@/components/loading-spinner';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Textarea } from '@/components/ui/textarea';
import {
    applyChanges,
    CommitConflicts,
    CommitSuccess,
    createEditConnectionUrl,
    DEFAULT_COLOR,
    DEFAULT_COMMIT_MESSAGE,
    DEFAULT_DRAW_STATE,
    fetchProjectState,
    RebaseStrategy,
    UpdateAction,
} from '@/state';
import { useQuery } from '@tanstack/react-query';
import { RefreshCw } from 'lucide-react';
import { MutableRefObject, useEffect, useRef, useState } from 'react';
import { Link, useParams, useSearchParams } from 'react-router';

export default function Project() {
    const { projectId } = useParams();
    const [searchParams, _setSearchParams] = useSearchParams();

    const editConnection: MutableRefObject<WebSocket | null> =
        useRef<WebSocket>(null);
    const [isEditing, setIsEditing] = useState(false);
    const [commitPending, setCommitPending] = useState(false);
    const [currentColor, setCurrentColor] = useState(DEFAULT_COLOR);
    const [commitMessage, setCommitMessage] = useState(DEFAULT_COMMIT_MESSAGE);
    const [actions, setActions] = useState<UpdateAction[]>([]);
    const [conflictedChunks, setConflictedChunks] = useState<number[] | null>(
        null,
    );
    const [rebaseStrategy, setRebaseStrategy] =
        useState<RebaseStrategy>('ours');

    const version = searchParams.get('version');

    const query = useQuery({
        queryKey: ['project', { projectId }, 'version', version],
        queryFn: async () => {
            if (!projectId) throw new Error('No project id found!');
            return await fetchProjectState(projectId, version);
        },
    });

    useEffect(() => {
        if (!projectId || !isEditing) {
            return;
        }

        const editorUrl = createEditConnectionUrl(projectId);
        editConnection.current = new WebSocket(editorUrl);

        editConnection.current.onmessage = (e) => {
            const result: CommitSuccess | CommitConflicts = JSON.parse(e.data);
            if ('conflicted_chunks' in result) {
                setConflictedChunks(result.conflicted_chunks);
            } else {
                setIsEditing(false);
                setActions([]);
                setConflictedChunks(null);
                query.refetch();
            }
            setCommitPending(false);
        };

        return () => {
            if (editConnection.current?.readyState === WebSocket.OPEN) {
                editConnection.current.close();
                editConnection.current = null;
            }
        };
    }, [isEditing, projectId]);

    return (
        <div className="container flex flex-col mx-auto p-4">
            <div className="flex flex-row items-center justify-between py-4 align-middle text-center h-16 mt-4 mb-8">
                <h2 className="text-xl font-bold mt-8 mb-4">
                    <a
                        className="hover:text-blue-400 underline"
                        href={`/project/${projectId}`}
                    >
                        Project {projectId?.split('-')[0]}
                    </a>
                </h2>
                <div className="flex flex-row space-x-2 ps-2">
                    {!isEditing && (
                        <Button onClick={() => query.refetch()}>
                            <RefreshCw color="white" />
                        </Button>
                    )}
                    {!isEditing && (
                        <Button
                            onClick={() => {
                                if (!projectId) return;
                                const queryParams = `?scale=20${
                                    version ? `&version=${version}` : ''
                                }`;
                                window
                                    ?.open(
                                        `/projects/${projectId}/img${queryParams}`,
                                        '_blank',
                                    )
                                    ?.focus();
                            }}
                        >
                            Export
                        </Button>
                    )}
                    {!searchParams.get('version') && !isEditing && (
                        <Button
                            onClick={async () => {
                                await query.refetch();
                                setIsEditing(true);
                            }}
                        >
                            Edit
                        </Button>
                    )}
                </div>
            </div>
            <div className="flex flex-row flex-wrap gap-x-8 gap-y-4">
                <div className="flex w-full md:w-1/2 lg:w-7/12 aspect-square">
                    <Grid
                        colors={applyChanges(
                            (query.data?.state ?? DEFAULT_DRAW_STATE).chunks,
                            actions,
                        )}
                        cols={query.data?.state.cols ?? 16}
                        rows={query.data?.state.rows ?? 16}
                        conflictedColor="lime"
                        conflictedIndices={conflictedChunks ?? []}
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
                </div>
                <div className="md:w-1/3 lg:w-1/4 w-full md:overflow-scroll aspect-square">
                    {isEditing && (
                        <div className="flex flex-col space-y-4">
                            <h3 className="text-lg font-medium">Edit</h3>
                            {!conflictedChunks && (
                                <ColorPicker
                                    selectedColor={currentColor}
                                    onColorChange={setCurrentColor}
                                />
                            )}
                            {conflictedChunks && (
                                <div className="bg-red-200 p-4 rounded-md">
                                    <p>
                                        Conflicts were found while committing
                                        your changes. You can choose to resolve
                                        the conflicted chunks by preferring the
                                        changes you have made, or the ones made
                                        by others
                                    </p>
                                </div>
                            )}
                            <Label htmlFor="commit-message">Message</Label>
                            <Textarea
                                id="commit-message"
                                placeholder="Updated some pixels"
                                value={commitMessage}
                                onChange={(e) =>
                                    setCommitMessage(e.target.value)
                                }
                            />
                            {conflictedChunks && (
                                <div className="flex flex-col space-y-2">
                                    <Label htmlFor="rebase-strategy">
                                        Resolve conflicts using:
                                    </Label>
                                    <RadioGroup
                                        id="rebase-strategy"
                                        defaultValue="ours"
                                        value={rebaseStrategy}
                                        onValueChange={(value) =>
                                            setRebaseStrategy(
                                                value as RebaseStrategy,
                                            )
                                        }
                                    >
                                        <div className="flex items-center flex-row space-x-2">
                                            <RadioGroupItem
                                                value="ours"
                                                id="rebase-ours"
                                                style={{
                                                    backgroundColor:
                                                        rebaseStrategy ===
                                                        'ours'
                                                            ? 'black'
                                                            : 'white',
                                                }}
                                            />
                                            <Label
                                                htmlFor="rebase-ours"
                                                style={{
                                                    fontWeight:
                                                        rebaseStrategy ===
                                                        'ours'
                                                            ? 'bold'
                                                            : 'normal',
                                                }}
                                            >
                                                Our Changes
                                            </Label>
                                        </div>
                                        <div className="flex items-center flex-row space-x-2">
                                            <RadioGroupItem
                                                value="theirs"
                                                id="rebase-theirs"
                                                style={{
                                                    backgroundColor:
                                                        rebaseStrategy ===
                                                        'theirs'
                                                            ? 'black'
                                                            : 'white',
                                                }}
                                            />
                                            <Label
                                                htmlFor="rebase-theirs"
                                                style={{
                                                    fontWeight:
                                                        rebaseStrategy ===
                                                        'theirs'
                                                            ? 'bold'
                                                            : 'normal',
                                                }}
                                            >
                                                Their Changes
                                            </Label>
                                        </div>
                                    </RadioGroup>
                                </div>
                            )}
                            <Button
                                onClick={() => {
                                    if (!editConnection.current) {
                                        console.error(
                                            'No active editing session!',
                                        );
                                        setIsEditing(false);
                                        return;
                                    }

                                    setCommitPending(true);

                                    if (conflictedChunks) {
                                        const command = {
                                            message: commitMessage,
                                            strategy: rebaseStrategy,
                                        };

                                        editConnection.current.send(
                                            JSON.stringify(command),
                                        );
                                        return;
                                    } else {
                                        // Send commit command to websocket
                                        const command = {
                                            message: commitMessage,
                                            changes: actions,
                                        };

                                        editConnection.current.send(
                                            JSON.stringify(command),
                                        );
                                    }
                                }}
                            >
                                {commitPending && (
                                    <div className="flex flex-row space-x-2 items-center align-middle">
                                        <a>Committing</a>
                                        <LoadingSpinner
                                            size={16}
                                            color="white"
                                            borderWidth={2}
                                        />
                                    </div>
                                )}
                                {!commitPending &&
                                    (conflictedChunks
                                        ? 'Rebase & Commit'
                                        : 'Commit')}
                            </Button>
                            {!commitPending && (
                                <Button
                                    variant={'destructive'}
                                    onClick={() => {
                                        setActions([]);
                                        setCommitMessage(
                                            DEFAULT_COMMIT_MESSAGE,
                                        );
                                        setConflictedChunks(null);
                                        setIsEditing(false);
                                        setCommitPending(false);
                                    }}
                                >
                                    Cancel
                                </Button>
                            )}
                        </div>
                    )}
                    {!isEditing && (
                        <div className="flex flex-col w-full">
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
        </div>
    );
}
