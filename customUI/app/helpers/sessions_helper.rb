module SessionsHelper

    def log_in
        session[:user_id] = 1
    end    
    
    def log_out
        session.delete(1)
    end    
end
