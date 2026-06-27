import { useState } from "react";
import { SettingsItem } from "./settings-item";
import { Key } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { updateProject } from "@/lib/api/project";
import { useMetaInfo } from "@/components/context/metainfo";

export function LlmConfigEditor() {
  const { activeProject, accessToken, reloadActiveProject } = useMetaInfo();
  const [llmApiKey, setLlmApiKey] = useState(activeProject.llm_api_key || "");
  const [llmBaseUrl, setLlmBaseUrl] = useState(activeProject.llm_base_url || "");
  const [llmModel, setLlmModel] = useState(activeProject.llm_model || "");
  const [isUpdating, setIsUpdating] = useState(false);

  const handleSaveLlmConfig = async () => {
    setIsUpdating(true);
    try {
      await updateProject(
        accessToken,
        activeProject.id,
        activeProject.name,
        llmApiKey,
        llmBaseUrl,
        llmModel
      );
      await reloadActiveProject();
      toast.success("AI Settings updated");
    } catch (error) {
      console.error("Failed to update AI settings:", error);
      toast.error("Failed to update AI settings");
    } finally {
      setIsUpdating(false);
    }
  };

  return (
    <SettingsItem
      icon={Key}
      label="AI Settings (BYOK)"
      description={
        <div className="flex flex-col gap-4 mt-2">
          <p className="text-sm text-muted-foreground mb-2">
            Configure your own LLM provider (Groq, OpenRouter, etc.).<br/>
            <span className="font-medium text-orange-500">Free messages used: {activeProject.message_count || 0} / 10</span>
          </p>
          <div className="flex flex-col gap-2 max-w-[400px]">
            <Input
              placeholder="API Key (e.g. gsk_... or sk-or-v1...)"
              value={llmApiKey}
              onChange={(e) => setLlmApiKey(e.target.value)}
              disabled={isUpdating}
              type="password"
            />
            <Input
              placeholder="Base URL (e.g. https://api.groq.com/openai/v1)"
              value={llmBaseUrl}
              onChange={(e) => setLlmBaseUrl(e.target.value)}
              disabled={isUpdating}
            />
            <Input
              placeholder="Model (e.g. llama3-70b-8192)"
              value={llmModel}
              onChange={(e) => setLlmModel(e.target.value)}
              disabled={isUpdating}
            />
            <Button 
              onClick={handleSaveLlmConfig} 
              disabled={isUpdating}
              className="w-full mt-2"
            >
              Save AI Settings
            </Button>
          </div>
        </div>
      }
    />
  );
}
