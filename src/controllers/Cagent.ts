import { Request, Response } from 'express';
import Retell from 'retell-sdk';
import ExpressError from '../utils/ExpressError';

// Retell 클라이언트 초기화 (환경변수에서 API 키 가져오기)
const getRetellClient = (apiKey?: string) => {
  const key = apiKey || process.env.RetellApiKey;
  if (!key) {
    throw new ExpressError('Retell API 키가 설정되지 않았습니다.', 500);
  }
  return new Retell({ apiKey: key });
};

// Create Agent
export const createAgent = async (req: Request, res: Response) => {
  const client = getRetellClient(req.body.apiKey);

  const agentResponse = await client.agent.create({
    response_engine: req.body.response_engine,
    voice_id: req.body.voice_id,
    ...req.body.agent,
  });

  res.status(201).json({
    success: true,
    agent: agentResponse,
  });
};

// Get Agent
export const getAgent = async (req: Request, res: Response) => {
  const client = getRetellClient(req.query.apiKey as string);
  const { id } = req.params;

  const agentResponse = await client.agent.retrieve(id);

  res.json({
    success: true,
    agent: agentResponse,
  });
};

// List Agents
export const listAgents = async (req: Request, res: Response) => {
  const client = getRetellClient(req.query.apiKey as string);

  const agentsResponse = await client.agent.list();

  res.render('agent/agent', { agents: agentsResponse });
};

// Update Agent
export const updateAgent = async (req: Request, res: Response) => {
  const client = getRetellClient(req.body.apiKey);
  const { id } = req.params;

  const agentResponse = await client.agent.update(id, {
    response_engine: req.body.response_engine,
    voice_id: req.body.voice_id,
    ...req.body.agent,
  });

  res.json({
    success: true,
    agent: agentResponse,
  });
};

// Delete Agent
export const deleteAgent = async (req: Request, res: Response) => {
  const client = getRetellClient(req.body.apiKey || (req.query.apiKey as string));
  const { id } = req.params;

  await client.agent.delete(id);

  res.json({
    success: true,
    message: '에이전트가 성공적으로 삭제되었습니다.',
  });
};

// Get Agent Versions (Retell AI에서 지원하는 경우)
export const getAgentVersions = async (req: Request, res: Response) => {
  const client = getRetellClient(req.query.apiKey as string);
  const { id } = req.params;

  const versionsResponse =
    (await client.agent.getVersions?.(id)) || (await client.agent.retrieve(id));

  res.json({
    success: true,
    agentId: id,
    versions: versionsResponse,
  });
};
