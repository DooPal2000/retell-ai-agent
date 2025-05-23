import express from 'express';
import passport from 'passport';
import { Router } from 'express';

import catchAsync from '../utils/catchAsync';
// import { isLoggedIn, isSecureAdminCreation, isAuthorized, isRealPhone } from '../middleware';
import * as agents from '../controllers/Cagent';

const router: Router = express.Router();

// Create Agent
router.post('/', catchAsync(agents.createAgent));

// Get Agent
router.get('/:id', catchAsync(agents.getAgent));

// List Agents
router.get('/', catchAsync(agents.listAgents));

// Update Agent
router.patch('/:id', catchAsync(agents.updateAgent));

// Delete Agent
router.delete('/:id', catchAsync(agents.deleteAgent));

// Get Agent Versions
router.get('/:id/versions', catchAsync(agents.getAgentVersions));

export default router;
