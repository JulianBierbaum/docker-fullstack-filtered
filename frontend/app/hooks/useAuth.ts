"use client";
import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";

interface AuthState {
    role: string | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    isAdmin: boolean;
    isOrganizer: boolean;
    isVisitor: boolean;
}

export function useAuth(): AuthState & { logout: () => void } {
    const [role, setRole] = useState<string | null>(null);
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [isLoading, setIsLoading] = useState(true);
    const router = useRouter();

    useEffect(() => {
        const token = localStorage.getItem("token");
        if (token) {
            try {
                // Decode JWT payload
                const payload = JSON.parse(atob(token.split(".")[1]));

                // Check if token is expired
                const now = Math.floor(Date.now() / 1000);
                if (payload.exp && payload.exp < now) {
                    localStorage.removeItem("token");
                    setIsAuthenticated(false);
                    setRole(null);
                } else {
                    setRole(payload.role);
                    setIsAuthenticated(true);
                }
            } catch (e) {
                localStorage.removeItem("token");
                setIsAuthenticated(false);
                setRole(null);
            }
        }
        setIsLoading(false);
    }, []);

    const logout = useCallback(() => {
        localStorage.removeItem("token");
        setRole(null);
        setIsAuthenticated(false);
        router.push("/login");
    }, [router]);

    return {
        role,
        isAuthenticated,
        isLoading,
        isAdmin: role === "admin",
        isOrganizer: role === "organizer",
        isVisitor: role === "visitor",
        logout,
    };
}
