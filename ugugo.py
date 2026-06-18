import asyncio
from mavsdk import System


WAYPOINTS = [
    {"name": "Waypoint 1", "lat": 47.398164, "lon": 8.546238},
    {"name": "Waypoint 2", "lat": 47.398238, "lon": 8.546031},
    
]

FLIGHT_ALTITUDE = 5.0   # Flight altitude (meters)
FLIGHT_SPEED = 8.0      # Flight speed (m/s)
HOVER_TIME = 5           # Hover time at each waypoint (seconds)


async def wait_for_connection(drone):
    print("Waiting for drone connection...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("Drone connected!")
            break


async def wait_for_gps(drone):
    print(" Checking GPS...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("GPS is ready!")
            break


async def check_battery(drone):
    async for battery in drone.telemetry.battery():
        level = battery.remaining_percent * 100

        if level >= 75:
            print(f"Battery Excellent: {level:.0f}%")
        elif level >= 40:
            print(f"Battery Good: {level:.0f}%")
        elif level >= 20:
            print(f"Warning! Low Battery: {level:.0f}%")
        else:
            print(f"Critical Battery! Land Immediately: {level:.0f}%")

        return level


async def goto_waypoint(drone, home_alt, wp):
    print(f"\n Navigating to: {wp['name']}")
    print(f"   📍 Lat: {wp['lat']}, Lon: {wp['lon']}")

    await drone.action.goto_location(
        latitude_deg=wp["lat"],
        longitude_deg=wp["lon"],
        absolute_altitude_m=home_alt + FLIGHT_ALTITUDE,
        yaw_deg=0
    )

    # Wait until arrival
    async for position in drone.telemetry.position():
        dist_lat = abs(position.latitude_deg - wp["lat"])
        dist_lon = abs(position.longitude_deg - wp["lon"])

        if dist_lat < 0.0001 and dist_lon < 0.0001:
            print(f" Arrived at {wp['name']}")
            break

    await asyncio.sleep(HOVER_TIME)


async def main():
    drone = System()
    await drone.connect(system_address="udp://:14540")

    await wait_for_connection(drone)
    await wait_for_gps(drone)
    await check_battery(drone)

    # Get home altitude
    home = await anext(drone.telemetry.home())
    home_alt = home.absolute_altitude_m

    print(f"\n Home Altitude: {home_alt:.1f} m")

    # Arm the drone
    print("\nArming motors...")
    await drone.action.arm()

    # Takeoff
    await drone.action.set_takeoff_altitude(10)
    print("Taking off...")
    await drone.action.takeoff()

    async for state in drone.telemetry.landed_state():
        if state == state.IN_AIR:
            print("Drone is airborne!")
            break

    await asyncio.sleep(3)

    # Visit all waypoints
    print(f"\n Mission Plan: {len(WAYPOINTS)} Waypoints")

    for i, wp in enumerate(WAYPOINTS, 1):
        print(f"\n─── Waypoint {i}/{len(WAYPOINTS)} ───")
        await check_battery(drone)
        await goto_waypoint(drone, home_alt, wp)

    # Return to Launch
    print("\nReturning to Launch...")
    await drone.action.return_to_launch()

    async for state in drone.telemetry.landed_state():
        if state == state.ON_GROUND:
            print("Drone landed safely!")
            break

    print("\n Mission completed successfully!") 
    print("\n Mission completed successfully!") 


if __name__ == "__main__":
    asyncio.run(main())


    