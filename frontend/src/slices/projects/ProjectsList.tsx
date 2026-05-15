import { Link } from "react-router";
import { useCallback, useRef, type UIEvent } from "react";
import moment from "moment";

import "./ProjectsList.scss";
import { useGetAllOwnedProjectsQuery } from "../api/slice";
import { Spinner } from "../../shared/components";
import { CreateProjectButton } from "./CreateProjectButton";
import { Tooltip } from "../../shared/components/tooltip/Tooltip";
import { useTranslation } from "react-i18next";

export function ProjectsList() {
  const { t } = useTranslation();
  const { data, isLoading, isError } = useGetAllOwnedProjectsQuery();
  const listRef = useRef<HTMLDivElement>(null);
  const handleScroll = useCallback((e: UIEvent) => {
    if (!listRef.current) return;

    if (e.currentTarget.scrollTop > 1) {
      listRef.current.classList.add("projects-list__top-shadow");
    } else {
      listRef.current.classList.remove("projects-list__top-shadow");
    }

    if (
      e.currentTarget.scrollTop + e.currentTarget.clientHeight + 1 <
      e.currentTarget.scrollHeight
    ) {
      listRef.current.classList.add("projects-list__bottom-shadow");
    } else {
      listRef.current.classList.remove("projects-list__bottom-shadow");
    }
  }, []);

  if (isLoading) {
    return (
      <div className="projects-list__message">
        <Spinner />
      </div>
    );
  }

  if (isError) {
    return (
      <div className="projects-list__message">
        Unfortunately, something went wrong. Try refreshing the page.
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="projects-list__message">
        <div>
          You don't have any{" "}
          <Tooltip
            content={
              <p style={{ fontWeight: 400 }}>
                A <b>project</b> is a workspace where you can probe different
                interior designs.
              </p>
            }
            position="top"
          >
            <div
              style={{
                display: "inline-block",
                textDecoration: "underline dotted",
                textUnderlineOffset: "5px",
              }}
            >
              projects
            </div>
          </Tooltip>{" "}
          yet
        </div>
        <CreateProjectButton />
      </div>
    );
  }

  return (
    <div className="projects-list">
      <CreateProjectButton />
      <div className="projects-list__container" ref={listRef}>
        <div className="projects-list__list" onScroll={handleScroll}>
          {data.map((project) => (
            <Link
              className="projects-list__item"
              to={`/editor/project/${project.id}`}
              key={project.id}
            >
              <div>
                {project.name ||
                  t(
                    "Projects.ProjectsList.DefaultProjectName",
                    "Untitiled project",
                  )}
              </div>
              <div className="projects-list__info">
                <p>
                  {project.plansCount} / {project.plansLimit} plans
                </p>{" "}
                <span />
                <p>{moment(project.dtUpdated).fromNow()}</p>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
