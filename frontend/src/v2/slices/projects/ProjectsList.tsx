import "./ProjectsList.scss";
import { useGetAllOwnedProjectsQuery } from "../api/slice";
import { DeleteProjectButton } from "./DeleteProjectButton";
import { ShareProjectButton } from "./ShareProjectButton";

export function ProjectsList() {
  const { data, isLoading } = useGetAllOwnedProjectsQuery();
  if (isLoading) {
    return <div>Loading</div>;
  }
  if (!data) {
    return <div>No data</div>;
  }
  return (
    <table>
      <thead>
        <tr>
          <th>Name</th>
          <th>Created At</th>
          <th>Updated At</th>
          <th>Fast Actions</th>
        </tr>
      </thead>
      <tbody>
        {data.map((project) => (
          <tr key={project.id}>
            <td>{project.name}</td>
            <td>{project.dtCreated}</td>
            <td>{project.dtUpdated}</td>
            <td>
              <DeleteProjectButton projectId={project.id} />
              <ShareProjectButton projectId={project.id} />
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
