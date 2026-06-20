import React, { useEffect, useState } from 'react'
import { Alert, Button, Card, Col, Form, Input, InputNumber, Radio, Row, Select, Slider, Space, Switch, Tag, Typography, message } from 'antd'
import { localClipApi, LocalClipConfiguration, LocalClipRunRequest } from '../services/localClipApi'

const { Title, Text, Paragraph } = Typography

const LocalClipPage: React.FC = () => {
  const [form] = Form.useForm<LocalClipRunRequest>()
  const [config, setConfig] = useState<LocalClipConfiguration | null>(null)
  const [running, setRunning] = useState(false)
  const [result, setResult] = useState<any>(null)

  useEffect(() => {
    localClipApi.configuration().then(setConfig).catch(() => message.error('读取本地切片配置失败'))
  }, [])

  const run = async (values: LocalClipRunRequest) => {
    setRunning(true)
    setResult(null)
    try {
      const data = await localClipApi.run(values)
      setResult(data)
      message.success(values.execute ? '切片任务完成' : '导出计划已生成')
    } catch (error: any) {
      message.error(error?.response?.data?.detail || '任务执行失败')
    } finally {
      setRunning(false)
    }
  }

  return (
    <div style={{ minHeight: 'calc(100vh - 64px)', background: 'var(--ac-bg)', padding: '32px 48px 64px' }}>
      <div style={{ maxWidth: 1180, margin: '0 auto' }}>
        <Space direction="vertical" size={18} style={{ width: '100%' }}>
          <div>
            <Title level={2} style={{ marginBottom: 4, color: 'var(--ac-ink)' }}>本地直播切片</Title>
            <Text style={{ color: 'var(--ac-sub)' }}>B站、抖音、TikTok 多平台预设；少量高质量切片；纯净版输出。</Text>
          </div>
          <Alert type="success" showIcon message={config?.privacy_notice || '所有视频只在本机处理，最终切片只从 clean.mp4 导出。'} />
          <Card title="任务配置">
            <Form form={form} layout="vertical" initialValues={{ platform: 'douyin', channel_mode: 'danmaku_file', layout: 'center', threshold: 0.45, merge_gap_seconds: 5, max_clips: 10, danmaku_delay_seconds: 10, execute: false, ffmpeg_path: 'ffmpeg' }} onFinish={run}>
              <Row gutter={20}>
                <Col xs={24} md={12}><Form.Item label="纯净版视频" name="clean_video_path" rules={[{ required: true }]} extra="最终输出只能来自 clean.mp4。"><Input placeholder="D:\\项目\\clean.mp4" /></Form.Item></Col>
                <Col xs={24} md={12}><Form.Item label="弹幕文件或分析输入" name="danmaku_path" rules={[{ required: true }]} extra="支持 B站 XML、JSON、JSONL、CSV。"><Input placeholder="D:\\项目\\danmaku.xml" /></Form.Item></Col>
              </Row>
              <Row gutter={20}>
                <Col xs={24} md={8}><Form.Item label="分析通道" name="channel_mode"><Select options={Object.entries(config?.channel_modes || {}).map(([value, label]) => ({ value, label }))} /></Form.Item></Col>
                <Col xs={24} md={8}><Form.Item label="目标平台" name="platform"><Select options={Object.values(config?.platforms || {}).map(item => ({ value: item.key, label: `${item.name} · ${item.aspect_ratio}` }))} /></Form.Item></Col>
                <Col xs={24} md={8}><Form.Item label="画面布局" name="layout"><Select options={[{ value: 'center', label: '居中裁切' }, { value: 'fit', label: '完整画面补边' }, { value: 'blur', label: '模糊背景适配' }]} /></Form.Item></Col>
              </Row>
              <Row gutter={20}>
                <Col xs={24} md={8}><Form.Item label="切片数量" name="max_clips"><Radio.Group options={(config?.clip_count_options || [5, 10, 15, 20, 25, 30]).map(value => ({ value, label: value }))} optionType="button" buttonStyle="solid" /></Form.Item></Col>
                <Col xs={24} md={8}><Form.Item label="高光阈值" name="threshold"><Slider min={0.2} max={0.9} step={0.05} marks={{ 0.2: '宽松', 0.45: '标准', 0.7: '严格' }} /></Form.Item></Col>
                <Col xs={24} md={8}><Form.Item label="弹幕延迟修正（秒）" name="danmaku_delay_seconds"><InputNumber min={0} max={60} style={{ width: '100%' }} /></Form.Item></Col>
              </Row>
              <Row gutter={20}>
                <Col xs={24} md={12}><Form.Item label="输出目录" name="output_dir" rules={[{ required: true }]}><Input placeholder="D:\\项目\\exports" /></Form.Item></Col>
                <Col xs={24} md={8}><Form.Item label="FFmpeg 路径" name="ffmpeg_path"><Input placeholder="ffmpeg" /></Form.Item></Col>
                <Col xs={24} md={4}><Form.Item label="实际导出" name="execute" valuePropName="checked"><Switch checkedChildren="导出" unCheckedChildren="预演" /></Form.Item></Col>
              </Row>
              <Button type="primary" htmlType="submit" loading={running} size="large">开始分析与切片</Button>
            </Form>
          </Card>
          <Card title="平台预设与安全区">
            <Row gutter={[16, 16]}>
              {Object.values(config?.platforms || {}).map(item => (
                <Col xs={24} md={8} key={item.key}><Card size="small" style={{ height: '100%' }}><Space direction="vertical"><Space><Text strong>{item.name}</Text><Tag>{item.aspect_ratio}</Tag></Space><Text type="secondary">{item.width} × {item.height} · {item.fps}fps</Text><Paragraph type="secondary" style={{ marginBottom: 0 }}>安全区：上 {item.safe_top}px / 下 {item.safe_bottom}px / 左 {item.safe_left}px / 右 {item.safe_right}px</Paragraph></Space></Card></Col>
              ))}
            </Row>
          </Card>
          {result && <Card title="执行结果"><Text>识别高光：{result.highlights?.length || 0} 条</Text><pre style={{ marginTop: 12, maxHeight: 420, overflow: 'auto', whiteSpace: 'pre-wrap' }}>{JSON.stringify(result, null, 2)}</pre></Card>}
        </Space>
      </div>
    </div>
  )
}

export default LocalClipPage
