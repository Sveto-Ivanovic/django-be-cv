import contactEndpointController from "./contact";
import userManagementEndpointController from "./usermanagement";
import userSupabaseEndpointController from '../services/vector_store/supabase_namespaces'
import userPineconeEndpointController from '../services/vector_store/pinecone_indexes'

export const globalAPI = {
  contact: contactEndpointController,
  userManagment: userManagementEndpointController,
  userSupabase: userSupabaseEndpointController,
  userPinecone: userPineconeEndpointController
};