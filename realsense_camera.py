import pyrealsense2 as rs
import cv2
import numpy as np
import sys

print("程序已启动")
print("退出方式:")
print("1. 在RGB/Depth窗口按ESC或数字2")
print("2. 在RGB窗口双击鼠标")
print("3. 点击窗口关闭按钮")
print("4. 在控制台按Ctrl+C")

distance = 0.0
depth_frame = None

def mouse_click(event, x, y, flags, param):
    global distance, depth_frame
    if event == cv2.EVENT_LBUTTONDOWN and depth_frame is not None:
        distance = depth_frame.get_distance(x, y)
        print(f"距离: {distance:.3f}米")
    elif event == cv2.EVENT_LBUTTONDBLCLK:
        print("双击退出")
        cv2.destroyAllWindows()
        return

def main():
    global distance, depth_frame
    
    # 配置相机
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    
    try:
        pipeline.start(config)
    except Exception as e:
        print(f"相机启动失败: {e}")
        return
    
    colorizer = rs.colorizer()
     
    # 创建窗口
    cv2.namedWindow("RGB")
    cv2.setMouseCallback("RGB", mouse_click)
    cv2.namedWindow("Depth", cv2.WINDOW_FULLSCREEN)
    cv2.namedWindow("Gray")
    
    running=True

    try:
        while running:
            # 获取帧
            frames = pipeline.wait_for_frames()
            color_frame = frames.get_color_frame()
            depth_frame = frames.get_depth_frame()
            
            if not color_frame or not depth_frame:
                continue
            
            # 处理图像
            color_img = np.asanyarray(color_frame.get_data())
            depth_colored = np.asanyarray(colorizer.colorize(depth_frame).get_data())
            depth_raw=np.asanyarray(depth_frame.get_data())
            depth_gray = cv2.normalize(depth_raw, None, 0, 255, cv2.NORM_MINMAX ,cv2.CV_8U)

            # 项目特色 ：可使用英文界面避免出现OpenCV中文代码"???", 采用cv2.FONT_HERSHEY_DUPLEX粗字体来作为视觉风格 
            # 如有中文显示需求, 可更改字体为cv2.FONT_HERSHEY_SIMPLEX 并恢复中文字体
            # 显示距离
            cv2.putText(color_img, f"Distance: {distance:.4f}m", 
                        (10, 40), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 255), 2)
            cv2.putText(color_img, "ESC/2: QUIT | DoubleClick: QUIT", 
                        (10, 80), cv2.FONT_HERSHEY_DUPLEX, 0.6, (0, 0, 255), 2)
            
            # 显示
            cv2.imshow("RGB", color_img)
            cv2.imshow("Depth", depth_colored)
            cv2.imshow("Gray", depth_gray)

            #新增：自动排版窗口位置，防止重叠
            cv2.moveWindow("RGB", 0, 0)
            cv2.moveWindow("Depth", 640 ,0)
            cv2.moveWindow("Gray", 1280 ,0)

            # 检测窗口是否被关闭
            if (cv2.getWindowProperty("RGB", cv2.WND_PROP_VISIBLE) < 1 or 
                cv2.getWindowProperty("Depth", cv2.WND_PROP_VISIBLE) < 1 or
                cv2.getWindowProperty("Gray", cv2.WND_PROP_VISIBLE) < 1):
                print("窗口被关闭，正在退出...")
                running = False
                break
            
            # 检测按键 - 等待33ms（约30FPS），同时检测按键
            key = cv2.waitKey(33) & 0xFF
            
            if key == 27 or key == ord('2'):  # ESC 或 2
                print(f"按键{'ESC' if key == 27 else '2'}退出")
                break
                
    except KeyboardInterrupt:
        print("\nCtrl+C退出")
    except Exception as e:
        print(f"错误: {e}")
    finally:
        print("释放资源...")
        pipeline.stop()
        cv2.destroyAllWindows()
        print("退出完成")

if __name__ == "__main__":
    main()