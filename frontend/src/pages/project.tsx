import { useParams } from "react-router";


export default function Project() {
    const { projectId } = useParams();

    return (
        <div>
            <h1>Project {projectId}</h1>
        </div>
    );
}