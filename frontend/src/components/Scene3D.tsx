import { useState, useRef } from "react";
import { Canvas } from "@react-three/fiber";
import { OrbitControls, Grid, Text } from "@react-three/drei";
import type { ThreeEvent } from "@react-three/fiber";
import type { Mesh } from "three";
import type { SceneObject } from "@/api/client.ts";
import { X } from "lucide-react";

interface SceneObjectMeshProps {
  obj: SceneObject;
  isSelected: boolean;
  onSelect: (obj: SceneObject) => void;
}

function SceneObjectMesh({ obj, isSelected, onSelect }: SceneObjectMeshProps) {
  const meshRef = useRef<Mesh>(null);
  const [hovered, setHovered] = useState(false);

  const handleClick = (e: ThreeEvent<MouseEvent>) => {
    e.stopPropagation();
    onSelect(obj);
  };

  const geometry = (() => {
    switch (obj.type) {
      case "cylinder":
        return <cylinderGeometry args={[0.5, 0.5, 1, 32]} />;
      case "sphere":
        return <sphereGeometry args={[0.5, 32, 32]} />;
      default:
        return <boxGeometry args={[1, 1, 1]} />;
    }
  })();

  return (
    <mesh
      ref={meshRef}
      position={obj.position}
      scale={obj.scale}
      onClick={handleClick}
      onPointerOver={() => setHovered(true)}
      onPointerOut={() => setHovered(false)}
    >
      {geometry}
      <meshStandardMaterial
        color={isSelected ? "#2563eb" : hovered ? "#60a5fa" : obj.color}
        transparent
        opacity={isSelected ? 1 : hovered ? 0.9 : 0.85}
      />
      <Text
        position={[0, obj.scale[1] / 2 + 0.3, 0]}
        fontSize={0.15}
        color="#334155"
        anchorX="center"
        anchorY="bottom"
      >
        {obj.name}
      </Text>
    </mesh>
  );
}

interface Scene3DProps {
  objects: SceneObject[];
}

export default function Scene3D({ objects }: Scene3DProps) {
  const [selected, setSelected] = useState<SceneObject | null>(null);

  return (
    <div className="relative w-full h-[400px] rounded-xl border border-border bg-surface overflow-hidden shadow-card">
      <Canvas
        camera={{ position: [8, 6, 8], fov: 50 }}
        onPointerMissed={() => setSelected(null)}
      >
        <ambientLight intensity={0.6} />
        <directionalLight position={[10, 10, 5]} intensity={0.8} castShadow />
        <directionalLight position={[-5, 5, -5]} intensity={0.3} />

        <Grid
          args={[20, 20]}
          cellSize={1}
          cellThickness={0.5}
          cellColor="#e2e8f0"
          sectionSize={5}
          sectionThickness={1}
          sectionColor="#cbd5e1"
          fadeDistance={30}
          position={[0, -0.01, 0]}
        />

        {objects.map((obj) => (
          <SceneObjectMesh
            key={obj.id}
            obj={obj}
            isSelected={selected?.id === obj.id}
            onSelect={setSelected}
          />
        ))}

        <OrbitControls
          enableDamping
          dampingFactor={0.05}
          minPolarAngle={0.2}
          maxPolarAngle={Math.PI / 2.1}
          minDistance={3}
          maxDistance={20}
        />
      </Canvas>

      {/* Info overlay */}
      {selected && (
        <div className="absolute bottom-4 left-4 right-4 max-w-sm bg-white/95 backdrop-blur rounded-lg shadow-modal p-4 animate-fade-in">
          <div className="flex items-start justify-between mb-2">
            <h4 className="text-sm font-semibold text-text-heading">
              {selected.name}
            </h4>
            <button
              onClick={() => setSelected(null)}
              className="p-0.5 hover:bg-surface-tertiary rounded transition-colors"
            >
              <X size={14} className="text-text-tertiary" />
            </button>
          </div>
          <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs">
            <div className="text-text-secondary">Type</div>
            <div className="text-text-primary font-medium">{selected.type}</div>
            <div className="text-text-secondary">Position</div>
            <div className="text-text-primary font-medium">
              {selected.position.map((v) => v.toFixed(1)).join(", ")}
            </div>
            {selected.metadata &&
              Object.entries(selected.metadata).map(([key, val]) => (
                <div key={key} className="contents">
                  <div className="text-text-secondary capitalize">{key.replace(/_/g, " ")}</div>
                  <div className="text-text-primary font-medium">{String(val)}</div>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* Legend */}
      <div className="absolute top-3 right-3 text-[10px] text-text-tertiary bg-white/80 backdrop-blur rounded-md px-2 py-1">
        Drag to orbit / Scroll to zoom
      </div>
    </div>
  );
}
