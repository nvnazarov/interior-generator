import { useCallback, useState } from "react";
import { useNavigate } from "react-router";

import {
  useCreateProjectMutation,
  useGetAllOwnedProjectsQuery,
} from "../api/slice";
import { Button } from "../../shared/components/button/Button";
import { useAppDispatch } from "../storeTypes";
import { notify } from "../notifications/slice";
import { PROJECTS_LIMIT } from "./lib";
import { Tooltip } from "../../shared/components";
import { useTranslation } from "react-i18next";

export function CreateProjectButton() {
  const { t } = useTranslation();
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const [createProject] = useCreateProjectMutation();
  const [processing, setProcessing] = useState(false);
  const { data: projects } = useGetAllOwnedProjectsQuery();

  const handleClick = useCallback(async () => {
    try {
      setProcessing(true);
      const project = await createProject().unwrap();
      navigate(`/editor/project/${project.id}`);
    } catch {
      dispatch(notify({ text: "Something went wrong", severity: "error" }));
    } finally {
      setProcessing(false);
    }
  }, []);

  const projectsLimitHit = projects && projects.length == PROJECTS_LIMIT;
  if (projectsLimitHit) {
    return (
      <Tooltip
        position="top"
        content={
          <p style={{ fontWeight: 400 }}>You've hit your projects limit</p>
        }
      >
        <Button
          onClick={handleClick}
          text={t("Projects.CreateProjectButton.Text", "Create project")}
          disabled
          primary
        />
      </Tooltip>
    );
  } else {
    return (
      <Button
        onClick={handleClick}
        text={t("Projects.CreateProjectButton.Text", "Create project")}
        disabled={processing}
        primary
      />
    );
  }
}
