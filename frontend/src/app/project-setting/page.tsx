"use client";

import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import { IdDisplay } from "@/components/apps/id-display";
import { BsQuestionCircle } from "react-icons/bs";
import { Check, Edit2 } from "lucide-react";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { useState, useEffect } from "react";
import { toast } from "sonner";
import { useMetaInfo } from "@/components/context/metainfo";
import { useUpdateProject } from "@/hooks/use-project";
import { Button } from "@/components/ui/button";
import { DeleteProjectDialog } from "@/components/project/delete-project-dialog";

export default function ProjectSettingPage() {
  const { activeProject } = useMetaInfo();
  const [projectName, setProjectName] = useState(activeProject.name);
  const [isEditingName, setIsEditingName] = useState(false);
  const [llmApiKey, setLlmApiKey] = useState(activeProject.llm_api_key || "");
  const [llmBaseUrl, setLlmBaseUrl] = useState(activeProject.llm_base_url || "");
  const [llmModel, setLlmModel] = useState(activeProject.llm_model || "");

  const { mutateAsync: updateProject, isPending: isProjectUpdating } =
    useUpdateProject();

  // Update state when active project changes
  useEffect(() => {
    setProjectName(activeProject.name);
    setLlmApiKey(activeProject.llm_api_key || "");
    setLlmBaseUrl(activeProject.llm_base_url || "");
    setLlmModel(activeProject.llm_model || "");
    setIsEditingName(false);
  }, [activeProject]);

  const handleSaveProjectName = async () => {
    if (!projectName.trim()) {
      toast.error("Project name cannot be empty");
      return;
    }

    // Only update if the name has actually changed
    if (projectName === activeProject.name) {
      setIsEditingName(false);
      return;
    }

    try {
      await updateProject({
        name: projectName,
      });
      setIsEditingName(false);
      toast.success("Project name updated");
    } catch (error) {
      console.error("Failed to update project name:", error);
      toast.error("Failed to update project name");
    }
  };

  const handleSaveLlmConfig = async () => {
    try {
      await updateProject({
        llm_api_key: llmApiKey,
        llm_base_url: llmBaseUrl,
        llm_model: llmModel,
      });
      toast.success("AI Settings updated");
    } catch (error) {
      console.error("Failed to update AI settings:", error);
      toast.error("Failed to update AI settings");
    }
  };

  return (
    <div className="w-full">
      <div className="flex items-center justify-between m-4">
        <h1 className="text-2xl font-semibold">Project settings</h1>
      </div>
      <Separator />

      <div className="px-4 py-6 space-y-6">
        {/* Project Name Section */}
        <div className="flex flex-row">
          <div className="flex flex-col items-left w-80">
            <label className="font-semibold">Project Name</label>
            <p className="text-sm text-muted-foreground">
              Change the name of the project
            </p>
          </div>
          <div className="flex items-center gap-2">
            <div className="relative">
              <Input
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
                className="w-96"
                disabled={!isEditingName || isProjectUpdating}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    handleSaveProjectName();
                  } else if (e.key === "Escape") {
                    setIsEditingName(false);
                    setProjectName(activeProject.name);
                  }
                }}
              />
            </div>
            {isEditingName ? (
              <Button
                size="sm"
                variant="ghost"
                onClick={handleSaveProjectName}
                className="h-8 w-8 p-0"
                disabled={isProjectUpdating}
              >
                <Check className="h-4 w-4" />
              </Button>
            ) : (
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="ghost"
                    onClick={() => setIsEditingName(true)}
                    className="h-8 w-8 p-0"
                  >
                    <Edit2 className="h-4 w-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>Click to edit project name</p>
                </TooltipContent>
              </Tooltip>
            )}
          </div>
        </div>

        <Separator />

        {/* AI Settings Section */}
        <div className="flex flex-row">
          <div className="flex flex-col items-left w-80">
            <div className="flex items-center gap-2">
              <label className="font-semibold">AI Settings (BYOK)</label>
              <Tooltip>
                <TooltipTrigger asChild>
                  <span className="cursor-pointer">
                    <BsQuestionCircle className="h-4 w-4 text-muted-foreground" />
                  </span>
                </TooltipTrigger>
                <TooltipContent side="top">
                  <p className="text-xs">Provide your own API Key to continue using the AI after the free tier limit is reached.</p>
                </TooltipContent>
              </Tooltip>
            </div>
            <p className="text-sm text-muted-foreground mt-1">
              Configure your own LLM provider (Groq, OpenRouter, etc.).<br/>
              <span className="font-medium text-orange-500">Free messages used: {activeProject.message_count || 0} / 10</span>
            </p>
          </div>
          <div className="flex flex-col gap-4 w-96">
            <Input
              placeholder="API Key (e.g. gsk_... or sk-or-v1...)"
              value={llmApiKey}
              onChange={(e) => setLlmApiKey(e.target.value)}
              disabled={isProjectUpdating}
              type="password"
            />
            <Input
              placeholder="Base URL (e.g. https://api.groq.com/openai/v1)"
              value={llmBaseUrl}
              onChange={(e) => setLlmBaseUrl(e.target.value)}
              disabled={isProjectUpdating}
            />
            <Input
              placeholder="Model (e.g. llama3-70b-8192)"
              value={llmModel}
              onChange={(e) => setLlmModel(e.target.value)}
              disabled={isProjectUpdating}
            />
            <Button 
              onClick={handleSaveLlmConfig} 
              disabled={isProjectUpdating}
              className="w-full"
            >
              Save AI Settings
            </Button>
          </div>
        </div>

        <Separator />

        {/* Project ID Section */}
        <div className="flex flex-row">
          <div className="flex flex-col items-left w-80">
            <div className="flex items-center gap-2">
              <label className="font-semibold">Project ID</label>
              <Tooltip>
                <TooltipTrigger asChild>
                  <span className="cursor-pointer">
                    <BsQuestionCircle className="h-4 w-4 text-muted-foreground" />
                  </span>
                </TooltipTrigger>
                <TooltipContent side="top">
                  <p className="text-xs">Unique identifier for your project.</p>
                </TooltipContent>
              </Tooltip>
            </div>
          </div>
          <div className="flex items-center px-2">
            <IdDisplay id={activeProject.id} dim={false} />
          </div>
        </div>
        <Separator />
        <div className="mt-8">
          <h2 className="text-lg font-semibold mb-4">Danger Zone</h2>
          <div className="border border-red-200 rounded-md bg-red-50">
            <div className="p-4 flex items-center justify-between">
              <div>
                <h3 className="font-medium">Delete this project</h3>
                <p className="text-sm text-gray-500 mt-1">
                  Once you delete a project, there is no going back. This action
                  permanently deletes the project and all related data.
                </p>
              </div>
              <DeleteProjectDialog projectName={activeProject.name} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
