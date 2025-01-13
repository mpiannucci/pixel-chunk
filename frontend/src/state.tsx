export interface DrawState {
    chunks: string[];
    rows: number;
    cols: number;
}

export interface ProjectVersion {
    id: string;
    date: Date;
    message: string;
}

export interface ProjectState {
    id: string;
    state: DrawState;
    versions: ProjectVersion[];
}

export interface UpdateAction {
    index: number;
    color: string;
}

export interface CommitCommand {
    message: string;
    changes: UpdateAction[];
}

export interface RebaseCommitCommand {
    message: string;
    strategy: RebaseStrategy;
}

export interface CommitSuccess {
    latest_snapshot: string;
}

export interface CommitConflicts {
    source_snapshot: string;
    failed_at_snapshot: string;
    conflicted_chunks: number[];
}

export type RebaseStrategy = 'ours' | 'theirs';

export const DEFAULT_DRAW_STATE: DrawState = {
    chunks: Array(256).fill('#ffffffff'),
    rows: 16,
    cols: 16,
};

export function indexToRowCol(index: number, cols: number) {
    return [Math.floor(index / cols), index % cols];
}

export function parseProjectVersion(json: any): ProjectVersion {
    return {
        ...json,
        date: new Date(json.date),
    };
}

export function parseProjectState(json: any): ProjectState {
    return {
        ...json,
        versions: json.versions.map(parseProjectVersion),
    };
}

export async function fetchProjectState(
    projectId: string,
    version: string | null,
): Promise<ProjectState> {
    const url = `/projects/${projectId}${version ? `?version=${version}` : ''}`;
    const response = await fetch(url);
    const json = await response.json();
    return parseProjectState(json);
}

export async function createNewProject(): Promise<string> {
    const response = await fetch('/projects/new', {
        method: 'post',
    });
    const json = await response.json();
    return json.id as string;
}

export function applyChanges(
    colors: string[],
    changes: UpdateAction[],
): string[] {
    const cloned = [...colors];
    changes.forEach((change) => (cloned[change.index] = change.color));
    return cloned;
}

export function createEditConnectionUrl(projectId: string): string {
    return `ws://localhost:8000/projects/${projectId}/edit`;
}

export const DEFAULT_COLOR = '#ffffffff';
export const DEFAULT_COMMIT_MESSAGE = 'Updated some pixels';
