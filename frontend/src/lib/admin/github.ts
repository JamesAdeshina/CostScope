export interface GitHubWorkflowRun {
  id: number;
  status: string;
  conclusion: string | null;
  created_at: string;
  updated_at: string;
  html_url: string;
}


interface GitHubWorkflowDispatchResponse {
  workflow_run_id: number;
  run_url: string;
  html_url: string;
}


function getConfig() {
  const token =
    process.env.GITHUB_ACTIONS_TOKEN;

  const owner =
    process.env.GITHUB_REPOSITORY_OWNER;

  const repo =
    process.env.GITHUB_REPOSITORY_NAME;

  const workflow =
    process.env.GITHUB_REFRESH_WORKFLOW;

  const branch =
    process.env.GITHUB_REFRESH_BRANCH ??
    "main";

  if (
    !token ||
    !owner ||
    !repo ||
    !workflow
  ) {
    throw new Error(
      "GitHub refresh configuration is incomplete.",
    );
  }

  return {
    token,
    owner,
    repo,
    workflow,
    branch,
  };
}


function headers(
  token: string,
): HeadersInit {
  return {
    Accept:
      "application/vnd.github+json",
    Authorization:
      `Bearer ${token}`,
    "X-GitHub-Api-Version":
      "2026-03-10",
    "Content-Type":
      "application/json",
  };
}


export async function
dispatchRefreshWorkflow(): Promise<GitHubWorkflowDispatchResponse> {
  const config =
    getConfig();

  const url =
    `https://api.github.com/repos/` +
    `${config.owner}/${config.repo}/` +
    `actions/workflows/` +
    `${config.workflow}/dispatches`;

  const response =
    await fetch(
      url,
      {
        method: "POST",
        headers:
          headers(config.token),
        body: JSON.stringify({
          ref: config.branch,
        }),
        cache: "no-store",
      },
    );

  if (!response.ok) {
    const body =
      await response.text();

    throw new Error(
      `GitHub workflow dispatch failed ` +
      `(${response.status}): ${body}`,
    );
  }

  return (
    await response.json()
  ) as GitHubWorkflowDispatchResponse;
}


export async function
getRefreshRun(
  runId: number,
): Promise<GitHubWorkflowRun> {
  const config =
    getConfig();

  const url =
    `https://api.github.com/repos/` +
    `${config.owner}/${config.repo}/` +
    `actions/runs/${runId}`;

  const response =
    await fetch(
      url,
      {
        headers:
          headers(config.token),
        cache: "no-store",
      },
    );

  if (!response.ok) {
    const body =
      await response.text();

    throw new Error(
      `GitHub workflow status failed ` +
      `(${response.status}): ${body}`,
    );
  }

  return (
    await response.json()
  ) as GitHubWorkflowRun;
}
