import contactEndpointController from "./contact";
import userManagementEndpointController from "./usermanagement";
import userSupabaseEndpointController from '../services/vector_store/supabase_namespaces'
import userPineconeEndpointController from '../services/vector_store/pinecone_indexes'
import userValidationEndpointController from './testcase'
import userChatbotEndpointController from './chatbot'


export const globalAPI = {
  contact: contactEndpointController,
  userManagment: userManagementEndpointController,
  userSupabase: userSupabaseEndpointController,
  userPinecone: userPineconeEndpointController,
  userEval: userValidationEndpointController,
  userChatbot: userChatbotEndpointController
};