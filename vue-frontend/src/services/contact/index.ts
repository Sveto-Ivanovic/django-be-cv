import http from '../axios_service/api'
import type { APIResponse } from '../axios_service/axiosTypes'
import type { SendContactInfo } from './types'
import { useMutation } from '@tanstack/vue-query'

// --- raw API calls (optional but nice to separate) ---
const api = {
  sendMessage: (req: SendContactInfo) =>
    http.post<APIResponse<string>>('messages/send-message/', req),
}

function useSendContactMessage() {
  return useMutation({
    mutationKey: ['contact', 'send'],
    mutationFn: (req: SendContactInfo) => api.sendMessage(req),
  })
}
/*
function useGetContacts() {
  return useQuery({
    queryKey: ['contact', 'list'],
    queryFn: () => api.getContacts(),
  })
}

function useDeleteContact() {
  return useMutation({
    mutationKey: ['contact', 'delete'],
    mutationFn: (id: string) => api.deleteContact(id),
  })
}
*/
export default {
  useSendContactMessage,
  /*useGetContacts,
  useDeleteContact,
  */
}