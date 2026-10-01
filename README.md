# ros2-unity-sim

A small distributed ROS 2 system that uses Unity as its simulation environment. A simulated distance sensor feeds a controller node that decides how fast a simulated robot may move, and the robot reacts in the Unity scene.

The scenario itself is deliberately simple. The point of the project is the communication between the parts: how messages travel between ROS 2 nodes, how they cross the boundary between ROS 2 and Unity, and what the system does when that communication degrades or stops.

## Status

**In progress.** Goal: predictable, safe behaviour when the distance sensor stops delivering data. Only the first node exists so far; the rest of this README describes the intended design and is updated as parts are built.

- [x] Fake distance source (`fake_distance_node`, Python)
- [ ] Mock actuator that logs velocity commands
- [ ] Watchdog: detect missing sensor data (timer or QoS deadline/liveliness)
- [ ] Speed controller as an explicit state machine:
      NORMAL → DEGRADED → SAFE_STOP → RECOVERY
- [ ] Unit tests for all state transitions
- [ ] Launch test: stop the sensor, verify speed drops to 0 within the deadline
- [ ] CI with `colcon test` in a `ros:jazzy` container
- [ ] State machine ported to C++ (logic without ROS dependencies, thin `rclcpp` wrapper)
- [ ] Unity scene connected through the ROS–TCP bridge

## Use of AI

All code in this repository is written by me. I use AI tools only to review code and to discuss design decisions, never to generate code. This README was drafted with AI assistance.

## Planned architecture

```mermaid
flowchart LR
    subgraph win["Windows host"]
        U["Unity scene<br/>simulated robot + distance sensor"]
    end
    subgraph wsl["WSL2 · Ubuntu 24.04 · ROS 2 Jazzy"]
        E["ros_tcp_endpoint"]
        F["fake_distance_node"]
        C["speed_controller<br/>watchdog + state machine"]
        M["mock_actuator"]
    end
    U <-- "TCP" --> E
    E -- "/distance" --> C
    F -. "/distance (stand-in for Unity)" .-> C
    C -- "/cmd_vel" --> E
    C -. "/cmd_vel (stand-in for Unity)" .-> M
```

- **Distance source** publishes readings on `/distance` (`sensor_msgs/Range`). There are two interchangeable sources behind the same topic and message type: a fake Python node that generates synthetic readings, and the Unity scene.
- **Speed controller** subscribes to `/distance` and publishes an allowed velocity on `/cmd_vel` (`geometry_msgs/Twist`). While readings arrive normally: full speed when the path is clear, slower as the obstacle gets closer, stop below a threshold. A watchdog notices when readings arrive late or stop, and an explicit state machine (NORMAL, DEGRADED, SAFE_STOP, RECOVERY) decides what the robot may do in each case. The controller is written in Python first; the state machine is later ported to C++ as a plain class without ROS dependencies, wrapped by a thin `rclcpp` node.
- **Actuator** is the simulated robot in Unity. Until the scene exists, a mock node logs the commands instead.
- **ROS–TCP endpoint**: Unity does not speak DDS. It connects over TCP to an endpoint node on the ROS 2 side, which republishes messages into the ROS 2 graph.

## Decisions so far

| Decision | Alternative | Reason |
|---|---|---|
| ROS 2 Jazzy | Humble, newer releases | Current LTS with support until 2029 and mature tooling |
| Python (rclpy) first, one node in C++ later | Everything in C++ | Learn the ROS 2 concepts without fighting the language at the same time; use C++ where it makes a difference |
| Port the controller's state machine to C++ | Port another node | It is the safety-relevant logic, and as a class without ROS dependencies it can be unit-tested in isolation |
| Explicit state machine in the controller | Ad-hoc timeout checks | Every reaction to missing data is a named state with defined transitions, so it can be tested and drawn as a diagram |
| Unity as simulator | Raspberry Pi with a real sensor | No hardware dependency, and scenarios can be repeated exactly |
| Unity rather than Gazebo | Gazebo (`ros_gz`) | Gazebo talks to ROS 2 natively; Unity needs a bridge, and crossing that boundary is one of the things this project looks at. Unity also runs natively on the Windows host |
| Swappable distance source | Unity only | Nodes can be developed and tested without Unity; real hardware could be added the same way |
| Standard message types | Custom messages | No separate interface package needed, and tools such as RViz can display the data without extra plugins |
| WSL2 | Native Linux (dual boot) | Unity runs on Windows; no real-time measurements are planned, so VM timing noise is acceptable |

## Non-goals

- No latency benchmarks or statistical performance analysis.
- No real hardware for now.
- No realistic physics or detailed Unity scene. The scene stays minimal.
- No navigation (Nav2), manipulation or ros2_control.
- Not a reusable library.

## Open questions

- Is the Unity ROS–TCP Connector still maintained and compatible with Jazzy and current Unity versions? The alternative is running ROS 2 natively inside Unity (for example Ros2ForUnity), which avoids the TCP hop but ties the build to platform-specific ROS 2 libraries.
- Which QoS guarantees survive the TCP bridge? The endpoint republishes messages with its own publishers, so QoS settings on the Unity side may not mean the same as between two ROS 2 nodes.
- How should the watchdog detect missing readings: QoS deadline and liveliness events, or a timer inside the node? Do the QoS events still fire when the data comes from Unity through the TCP endpoint?
- Where exactly are the limits between the states: how late may a reading be before the controller degrades, when does it stop, and how many good readings does recovery need?
- Networking between Windows and WSL2: default NAT or mirrored networking mode?
