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


export function indexToRowCol(index: number, cols: number) {
    return [Math.floor(index / cols), index % cols];
}

export function parseProjectVersion(json: any): ProjectVersion {
    return {
        ...json,
        date: new Date(json.date),
    }
}

export function parseProjectState(json: any): ProjectState {
    return {
        ...json, 
        versions: json.versions.map(parseProjectVersion),
    }
}

export const DEFAULT_DRAW_STATE: DrawState = {
    chunks: Array(256).fill('#ffffffff'),
    rows: 16,
    cols: 16,
}