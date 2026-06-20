import axios from 'axios'
import { apiConfigManager } from '../utils/apiConfig'

export interface LocalClipConfiguration {
  platforms: Record<string, {
    key: string
    name: string
    width: number
    height: number
    fps: number
    aspect_ratio: string
    safe_top: number
    safe_bottom: number
    safe_left: number
    safe_right: number
  }>
  clip_count_options: number[]
  layout_options: string[]
  channel_modes: Record<string, string>
  privacy_notice: string
}

export interface LocalClipRunRequest {
  clean_video_path: string
  danmaku_path: string
  platform: 'bilibili' | 'douyin' | 'tiktok'
  output_dir: string
  channel_mode: 'ocr_video' | 'danmaku_file'
  layout: 'center' | 'fit' | 'blur'
  threshold: number
  merge_gap_seconds: number
  max_clips: number
  danmaku_delay_seconds: number
  execute: boolean
  ffmpeg_path: string
}

const client = axios.create({ timeout: 300000 })
client.interceptors.request.use((config) => {
  config.baseURL = apiConfigManager.getBaseUrl()
  return config
})

export const localClipApi = {
  async configuration(): Promise<LocalClipConfiguration> {
    return (await client.get('/local-clips/configuration')).data
  },
  async run(payload: LocalClipRunRequest): Promise<any> {
    return (await client.post('/local-clips/run', payload)).data
  },
}
