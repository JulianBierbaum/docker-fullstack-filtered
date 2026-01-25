"use client";
import { createContext, useContext, useState, useEffect, useCallback, ReactNode } from "react";
import { useRouter } from "next/navigation";

interface AuthContextType {
    role: string | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    isAdmin: boolean;
    isOrganizer: boolean;
    isVisitor: boolean;
    logout: () => void;
    refreshAuth: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [role, setRole] = useState<string | null>(null);
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [isLoading, setIsLoading] = useState(true);
    const router = useRouter();

    const refreshAuth = useCallback(() => {
        const token = localStorage.getItem("token");
        if (token) {
            try {
                const payload = JSON.parse(atob(token.split(".")[1]));
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
        } else {
            setIsAuthenticated(false);
            setRole(null);
        }
        setIsLoading(false);
    }, []);

    useEffect(() => {
        refreshAuth();
    }, [refreshAuth]);

    const logout = useCallback(() => {
        localStorage.removeItem("token");
        setRole(null);
        setIsAuthenticated(false);
        router.push("/login");
    }, [router]);

    return (
        <AuthContext.Provider
            value={{
                role,
                isAuthenticated,
                isLoading,
                isAdmin: role === "admin",
                isOrganizer: role === "organizer",
                isVisitor: role === "visitor",
                logout,
                refreshAuth,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth(): AuthContextType {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return context;
}
