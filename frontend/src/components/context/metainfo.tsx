"use client";

import { Project } from "@/lib/types/project";
import {
  createContext,
  ReactNode,
  useContext,
  useState,
  useEffect,
  useCallback,
} from "react";
import { Skeleton } from "@/components/ui/skeleton";
import { useProjects, useReloadProjects } from "@/hooks/use-project";

// Dummy classes to replace PropelAuth
class DummyOrg {
  orgId = "107e06da-e857-4864-bc1d-4adcba02ab76";
  orgName = "Test Org";
  urlSafeOrgName = "test-org";
}

class DummyUser {
  userId = "test-user-123";
  email = "test@example.com";
  firstName = "Test";
  lastName = "User";
  getOrgs() { return [new DummyOrg()]; }
}

const dummyUser = new DummyUser() as any;

interface MetaInfoContextType {
  user: any;
  orgs: any[];
  activeOrg: any;
  setActiveOrg: (org: any) => void;
  projects: Project[];
  activeProject: Project;
  reloadActiveProject: () => Promise<void>;
  setActiveProject: (project: Project) => void;
  accessToken: string;
}

const MetaInfoContext = createContext<MetaInfoContextType | undefined>(
  undefined,
);

export const MetaInfoProvider = ({ children }: { children: ReactNode }) => {
    const userClass = dummyUser;
    const accessToken = "dummy_token";
    const refreshAuthInfo = async () => {};
    const [orgs, setOrgs] = useState<any[]>([]);
    const [activeOrg, setActiveOrg] = useState<any | null>(null);
    const [activeProject, setActiveProject] = useState<Project | null>(null);

    const { data: projects = [], isLoading: projectsLoading } = useProjects(
      activeOrg?.orgId,
      accessToken,
    );
    const reloadProjectsFunc = useReloadProjects();

    useEffect(() => {
      async function getOrgs() {
        // TODO: refactor this retry logic to use TanStack Query to
        // elegantly handle the loading and error state
        let retrievedOrgs = userClass.getOrgs();

        let attempts = 0;
        const maxAttempts = 5;

        // Wait for the default Personal Org to be created
        while (retrievedOrgs.length === 0 && attempts < maxAttempts) {
          await refreshAuthInfo();
          await new Promise((resolve) => setTimeout(resolve, 1000));
          retrievedOrgs = userClass.getOrgs();
          attempts++;
          console.log("retrievedOrgs", retrievedOrgs, attempts);
        }
        setOrgs(retrievedOrgs);
      }
      getOrgs();
    }, [userClass, refreshAuthInfo]);

    useEffect(() => {
      if (orgs.length > 0) {
        // TODO: get active org from local storage
        setActiveOrg(orgs[0]);
      }
    }, [orgs]);

    useEffect(() => {
      if (projects.length > 0) {
        const savedProjectId = localStorage.getItem(
          `activeProject_${activeOrg?.orgId}`,
        );
        const savedProject = savedProjectId
          ? projects.find((p) => p.id === savedProjectId)
          : null;

        setActiveProject(savedProject || projects[0]);
      }
    }, [projects, activeOrg]);

    useEffect(() => {
      if (activeProject && activeOrg) {
        localStorage.setItem(
          `activeProject_${activeOrg.orgId}`,
          activeProject.id,
        );
      }
    }, [activeProject, activeOrg]);

    const reloadActiveProject = useCallback(async () => {
      if (activeOrg && accessToken) {
        await reloadProjectsFunc(activeOrg.orgId);
      }
    }, [reloadProjectsFunc, activeOrg, accessToken]);

    return (
      <div>
        {activeOrg && activeProject && accessToken && !projectsLoading ? (
          <MetaInfoContext.Provider
            value={{
              user: userClass,
              orgs,
              activeOrg,
              setActiveOrg,
              projects,
              activeProject,
              setActiveProject,
              reloadActiveProject,
              accessToken,
            }}
          >
            {children}
          </MetaInfoContext.Provider>
        ) : (
          <div className="flex flex-col items-center justify-center min-h-screen space-y-3">
            <h1 className="text-2xl font-semibold">
              Setting up your workspace...
            </h1>
            <Skeleton className="h-[125px] w-[250px] rounded-xl" />
            <div className="space-y-2">
              <Skeleton className="h-4 w-[250px]" />
              <Skeleton className="h-4 w-[200px]" />
            </div>
          </div>
        )}
      </div>
    );
  };

export const useMetaInfo = () => {
  const context = useContext(MetaInfoContext);
  if (!context) {
    throw new Error("useMetaInfo must be used within a MetaInfoProvider");
  }
  return context;
};
